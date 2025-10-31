#include <functional>
#include <memory>
#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>
#include "lapjvs.h"

static char module_docstring[] =
    "This module wraps LAPJVS - Jonker-Volgenant linear sum assignment algorithm (Scalar-only, no AVX2/SIMD).";
static char lapjvs_native_docstring[] =
    "Solves the linear sum assignment problem following the input dtype (float32 or float64). Returns (row_ind, col_ind).";
static char lapjvs_float32_docstring[] =
    "Solves the linear sum assignment problem in float32 (casts inputs if needed). Returns (row_ind, col_ind).";
static char lapjvsa_native_docstring[] =
    "Solves the linear sum assignment problem following the input dtype (float32 or float64). Returns pairs (K,2).";
static char lapjvsa_float32_docstring[] =
    "Solves the linear sum assignment problem in float32 (casts inputs if needed). Returns pairs (K,2).";

static PyObject *py_lapjvs_native(PyObject *self, PyObject *args, PyObject *kwargs);
static PyObject *py_lapjvs_float32(PyObject *self, PyObject *args, PyObject *kwargs);
static PyObject *py_lapjvsa_native(PyObject *self, PyObject *args, PyObject *kwargs);
static PyObject *py_lapjvsa_float32(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef module_functions[] = {
  {"lapjvs", reinterpret_cast<PyCFunction>(py_lapjvs_native),
   METH_VARARGS | METH_KEYWORDS, lapjvs_native_docstring},
  {"lapjvs_native", reinterpret_cast<PyCFunction>(py_lapjvs_native),
   METH_VARARGS | METH_KEYWORDS, lapjvs_native_docstring},
  {"lapjvs_float32", reinterpret_cast<PyCFunction>(py_lapjvs_float32),
   METH_VARARGS | METH_KEYWORDS, lapjvs_float32_docstring},
  {"lapjvsa", reinterpret_cast<PyCFunction>(py_lapjvsa_native),
   METH_VARARGS | METH_KEYWORDS, lapjvsa_native_docstring},
  {"lapjvsa_native", reinterpret_cast<PyCFunction>(py_lapjvsa_native),
   METH_VARARGS | METH_KEYWORDS, lapjvsa_native_docstring},
  {"lapjvsa_float32", reinterpret_cast<PyCFunction>(py_lapjvsa_float32),
   METH_VARARGS | METH_KEYWORDS, lapjvsa_float32_docstring},
  {NULL, NULL, 0, NULL}
};

extern "C" {
PyMODINIT_FUNC PyInit__lapjvs(void) {
  static struct PyModuleDef moduledef = {
      PyModuleDef_HEAD_INIT,
      "lapjvs",
      module_docstring,
      -1,
      module_functions,
      NULL, NULL, NULL, NULL,
  };
  PyObject *m = PyModule_Create(&moduledef);
  if (m == NULL) {
    PyErr_SetString(PyExc_RuntimeError, "PyModule_Create() failed");
    return NULL;
  }
  import_array();
  return m;
}
}

template <typename O>
using pyobj_parent = std::unique_ptr<O, std::function<void(O*)>>;

template <typename O>
class _pyobj : public pyobj_parent<O> {
 public:
  _pyobj() : pyobj_parent<O>(nullptr, [](O *p){ if (p) Py_DECREF(p); }) {}
  explicit _pyobj(PyObject *ptr) : pyobj_parent<O>(
      reinterpret_cast<O *>(ptr), [](O *p){ if(p) Py_DECREF(p); }) {}
  void reset(PyObject *p) noexcept {
    pyobj_parent<O>::reset(reinterpret_cast<O*>(p));
  }
};

using pyobj = _pyobj<PyObject>;
using pyarray = _pyobj<PyArrayObject>;

template <typename F>
static always_inline void call_lap(int dim, const void *restrict cost_matrix,
                                   bool verbose,
                                   int *restrict row_ind, int *restrict col_ind,
                                   void *restrict v) {
  Py_BEGIN_ALLOW_THREADS
  auto cost_matrix_typed = reinterpret_cast<const F*>(cost_matrix);
  auto v_typed = reinterpret_cast<F*>(v);
  if (verbose) {
    lapjvs<true>(dim, cost_matrix_typed, row_ind, col_ind, v_typed);
  } else {
    lapjvs<false>(dim, cost_matrix_typed, row_ind, col_ind, v_typed);
  }
  Py_END_ALLOW_THREADS
}

// Zero-copy: preallocate NumPy outputs, write directly
static PyObject *py_lapjvs_native(PyObject *self, PyObject *args, PyObject *kwargs) {
  PyObject *cost_matrix_obj;
  int verbose = 0;
  static const char *kwlist[] = {"cost_matrix", "verbose", NULL};
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|p", const_cast<char**>(kwlist),
                                   &cost_matrix_obj, &verbose)) {
    return NULL;
  }

  pyarray cost_matrix_array(PyArray_FROM_OTF(cost_matrix_obj, NPY_NOTYPE, NPY_ARRAY_IN_ARRAY));
  if (!cost_matrix_array) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\" must be a numpy array");
    return NULL;
  }
  int typ = PyArray_TYPE(cost_matrix_array.get());
  if (typ != NPY_FLOAT32 && typ != NPY_FLOAT64) {
    PyErr_SetString(PyExc_TypeError, "\"cost_matrix\" must be float32 or float64");
    return NULL;
  }
  auto ndims = PyArray_NDIM(cost_matrix_array.get());
  if (ndims != 2) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\" must be a square 2D numpy array");
    return NULL;
  }
  auto dims = PyArray_DIMS(cost_matrix_array.get());
  if (dims[0] != dims[1]) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\" must be a square 2D numpy array");
    return NULL;
  }
  int dim = static_cast<int>(dims[0]);
  if (dim < 0) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\"'s shape is too large or invalid");
    return NULL;
  }

  if (dim == 0) {
    npy_intp ret_dims[] = {0};
    pyarray row_ind_array(PyArray_SimpleNew(1, ret_dims, NPY_INT));
    pyarray col_ind_array(PyArray_SimpleNew(1, ret_dims, NPY_INT));
    return Py_BuildValue("(OO)", row_ind_array.get(), col_ind_array.get());
  }

  auto cost_matrix = PyArray_DATA(cost_matrix_array.get());

  // Zero-copy outputs
  npy_intp ret_dims[] = {dim};
  pyarray row_ind_array(PyArray_SimpleNew(1, ret_dims, NPY_INT));
  pyarray col_ind_array(PyArray_SimpleNew(1, ret_dims, NPY_INT));
  auto row_ind = reinterpret_cast<int*>(PyArray_DATA(row_ind_array.get()));
  auto col_ind = reinterpret_cast<int*>(PyArray_DATA(col_ind_array.get()));

  if (typ == NPY_FLOAT32) {
    std::unique_ptr<float[]> v(new float[dim]);
    call_lap<float>(dim, cost_matrix, verbose, row_ind, col_ind, v.get());
  } else {
    std::unique_ptr<double[]> v(new double[dim]);
    call_lap<double>(dim, cost_matrix, verbose, row_ind, col_ind, v.get());
  }

  return Py_BuildValue("(OO)", row_ind_array.get(), col_ind_array.get());
}

// Zero-copy: write into NumPy outputs directly
static PyObject *py_lapjvs_float32(PyObject *self, PyObject *args, PyObject *kwargs) {
  PyObject *cost_matrix_obj;
  int verbose = 0;
  static const char *kwlist[] = {"cost_matrix", "verbose", NULL};
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|p", const_cast<char**>(kwlist),
                                   &cost_matrix_obj, &verbose)) {
    return NULL;
  }

  pyarray cost_matrix_array(PyArray_FROM_OTF(
      cost_matrix_obj, NPY_FLOAT32, NPY_ARRAY_IN_ARRAY | NPY_ARRAY_FORCECAST));
  if (!cost_matrix_array) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\" must be convertible to float32");
    return NULL;
  }

  auto ndims = PyArray_NDIM(cost_matrix_array.get());
  if (ndims != 2) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\" must be a square 2D numpy array");
    return NULL;
  }
  auto dims = PyArray_DIMS(cost_matrix_array.get());
  if (dims[0] != dims[1]) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\" must be a square 2D numpy array");
    return NULL;
  }
  int dim = static_cast<int>(dims[0]);
  if (dim < 0) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\"'s shape is too large or invalid");
    return NULL;
  }

  if (dim == 0) {
    npy_intp ret_dims[] = {0};
    pyarray row_ind_array(PyArray_SimpleNew(1, ret_dims, NPY_INT));
    pyarray col_ind_array(PyArray_SimpleNew(1, ret_dims, NPY_INT));
    return Py_BuildValue("(OO)", row_ind_array.get(), col_ind_array.get());
  }

  auto cost_matrix = PyArray_DATA(cost_matrix_array.get());

  // Zero-copy outputs
  npy_intp ret_dims[] = {dim};
  pyarray row_ind_array(PyArray_SimpleNew(1, ret_dims, NPY_INT));
  pyarray col_ind_array(PyArray_SimpleNew(1, ret_dims, NPY_INT));
  auto row_ind = reinterpret_cast<int*>(PyArray_DATA(row_ind_array.get()));
  auto col_ind = reinterpret_cast<int*>(PyArray_DATA(col_ind_array.get()));

  std::unique_ptr<float[]> v(new float[dim]);
  call_lap<float>(dim, cost_matrix, verbose, row_ind, col_ind, v.get());

  return Py_BuildValue("(OO)", row_ind_array.get(), col_ind_array.get());
}

// Zero-copy for pairs: write mapping into NumPy arrays directly, then build pairs
static PyObject *py_lapjvsa_native(PyObject *self, PyObject *args, PyObject *kwargs) {
  PyObject *cost_matrix_obj;
  int verbose = 0;
  static const char *kwlist[] = {"cost_matrix", "verbose", NULL};
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|p", const_cast<char**>(kwlist),
                                   &cost_matrix_obj, &verbose)) {
    return NULL;
  }

  pyarray cost_matrix_array(PyArray_FROM_OTF(cost_matrix_obj, NPY_NOTYPE, NPY_ARRAY_IN_ARRAY));
  if (!cost_matrix_array) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\" must be a numpy array");
    return NULL;
  }
  int typ = PyArray_TYPE(cost_matrix_array.get());
  if (typ != NPY_FLOAT32 && typ != NPY_FLOAT64) {
    PyErr_SetString(PyExc_TypeError, "\"cost_matrix\" must be float32 or float64");
    return NULL;
  }
  auto ndims = PyArray_NDIM(cost_matrix_array.get());
  if (ndims != 2) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\" must be a square 2D numpy array");
    return NULL;
  }
  auto dims = PyArray_DIMS(cost_matrix_array.get());
  if (dims[0] != dims[1]) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\" must be a square 2D numpy array");
    return NULL;
  }
  int dim = static_cast<int>(dims[0]);
  if (dim < 0) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\"'s shape is too large or invalid");
    return NULL;
  }
  auto cost_matrix = PyArray_DATA(cost_matrix_array.get());

  if (dim == 0) {
    npy_intp pdims[] = {0, 2};
    pyarray pairs(PyArray_SimpleNew(2, pdims, NPY_INT));
    return reinterpret_cast<PyObject*>(pairs.release());
  }

  // Zero-copy mapping outputs
  npy_intp odims[] = {dim};
  pyarray row_ind_array(PyArray_SimpleNew(1, odims, NPY_INT));
  pyarray col_ind_array(PyArray_SimpleNew(1, odims, NPY_INT));
  auto row_ind = reinterpret_cast<int*>(PyArray_DATA(row_ind_array.get()));
  auto col_ind = reinterpret_cast<int*>(PyArray_DATA(col_ind_array.get()));

  if (typ == NPY_FLOAT32) {
    std::unique_ptr<float[]> v(new float[dim]);
    call_lap<float>(dim, cost_matrix, verbose, row_ind, col_ind, v.get());
  } else {
    std::unique_ptr<double[]> v(new double[dim]);
    call_lap<double>(dim, cost_matrix, verbose, row_ind, col_ind, v.get());
  }

  // Count K
  npy_intp K = 0;
  for (int i = 0; i < dim; ++i) {
    int j = row_ind[i];
    if (j >= 0 && j < dim) ++K;
  }

  // Build pairs (K,2) directly
  npy_intp pdims[] = {K, 2};
  pyarray pairs(PyArray_SimpleNew(2, pdims, NPY_INT));
  auto* pdata = reinterpret_cast<int*>(PyArray_DATA(pairs.get()));
  npy_intp w = 0;
  for (int i = 0; i < dim; ++i) {
    int j = row_ind[i];
    if (j >= 0 && j < dim) {
      pdata[w * 2 + 0] = i;
      pdata[w * 2 + 1] = j;
      ++w;
    }
  }
  return reinterpret_cast<PyObject*>(pairs.release());
}

// Zero-copy for pairs (float32 path)
static PyObject *py_lapjvsa_float32(PyObject *self, PyObject *args, PyObject *kwargs) {
  PyObject *cost_matrix_obj;
  int verbose = 0;
  static const char *kwlist[] = {"cost_matrix", "verbose", NULL};
  if (!PyArg_ParseTupleAndKeywords(args, kwargs, "O|p", const_cast<char**>(kwlist),
                                   &cost_matrix_obj, &verbose)) {
    return NULL;
  }

  pyarray cost_matrix_array(PyArray_FROM_OTF(
      cost_matrix_obj, NPY_FLOAT32, NPY_ARRAY_IN_ARRAY | NPY_ARRAY_FORCECAST));
  if (!cost_matrix_array) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\" must be convertible to float32");
    return NULL;
  }
  auto ndims = PyArray_NDIM(cost_matrix_array.get());
  if (ndims != 2) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\" must be a square 2D numpy array");
    return NULL;
  }
  auto dims = PyArray_DIMS(cost_matrix_array.get());
  if (dims[0] != dims[1]) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\" must be a square 2D numpy array");
    return NULL;
  }
  int dim = static_cast<int>(dims[0]);
  if (dim < 0) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\"'s shape is too large or invalid");
    return NULL;
  }
  auto cost_matrix = PyArray_DATA(cost_matrix_array.get());

  if (dim == 0) {
    npy_intp pdims[] = {0, 2};
    pyarray pairs(PyArray_SimpleNew(2, pdims, NPY_INT));
    return reinterpret_cast<PyObject*>(pairs.release());
  }

  // Zero-copy mapping outputs
  npy_intp odims[] = {dim};
  pyarray row_ind_array(PyArray_SimpleNew(1, odims, NPY_INT));
  pyarray col_ind_array(PyArray_SimpleNew(1, odims, NPY_INT));
  auto row_ind = reinterpret_cast<int*>(PyArray_DATA(row_ind_array.get()));
  auto col_ind = reinterpret_cast<int*>(PyArray_DATA(col_ind_array.get()));

  std::unique_ptr<float[]> v(new float[dim]);
  call_lap<float>(dim, cost_matrix, verbose, row_ind, col_ind, v.get());

  // Count/build pairs
  npy_intp K = 0;
  for (int i = 0; i < dim; ++i) {
    int j = row_ind[i];
    if (j >= 0 && j < dim) ++K;
  }
  npy_intp pdims[] = {K, 2};
  pyarray pairs(PyArray_SimpleNew(2, pdims, NPY_INT));
  auto* pdata = reinterpret_cast<int*>(PyArray_DATA(pairs.get()));
  npy_intp w = 0;
  for (int i = 0; i < dim; ++i) {
    int j = row_ind[i];
    if (j >= 0 && j < dim) {
      pdata[w * 2 + 0] = i;
      pdata[w * 2 + 1] = j;
      ++w;
    }
  }
  return reinterpret_cast<PyObject*>(pairs.release());
}
