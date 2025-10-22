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

static PyObject *py_lapjvs_native(PyObject *self, PyObject *args, PyObject *kwargs);
static PyObject *py_lapjvs_float32(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef module_functions[] = {
  // Keep a friendly alias: lapjvs follows native dtype by default
  {"lapjvs", reinterpret_cast<PyCFunction>(py_lapjvs_native),
   METH_VARARGS | METH_KEYWORDS, lapjvs_native_docstring},
  {"lapjvs_native", reinterpret_cast<PyCFunction>(py_lapjvs_native),
   METH_VARARGS | METH_KEYWORDS, lapjvs_native_docstring},
  {"lapjvs_float32", reinterpret_cast<PyCFunction>(py_lapjvs_float32),
   METH_VARARGS | METH_KEYWORDS, lapjvs_float32_docstring},
  {NULL, NULL, 0, NULL}
};

extern "C" {
PyMODINIT_FUNC PyInit__lapjvs(void) {
  static struct PyModuleDef moduledef = {
      PyModuleDef_HEAD_INIT,
      "lapjvs",             /* m_name */
      module_docstring,     /* m_doc */
      -1,                   /* m_size */
      module_functions,     /* m_methods */
      NULL,                 /* m_reload */
      NULL,                 /* m_traverse */
      NULL,                 /* m_clear */
      NULL,                 /* m_free */
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
  _pyobj() : pyobj_parent<O>(
      nullptr, [](O *p){ if (p) Py_DECREF(p); }) {}
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

// Native dtype entry point: lapjvs_native(cost_matrix, verbose=False)
// - Accepts only float32 or float64 without casting; errors otherwise.
// - Dispatches to float or double kernel based on the input dtype.
// - Returns (row_ind, col_ind).
static PyObject *py_lapjvs_native(PyObject *self, PyObject *args, PyObject *kwargs) {
  PyObject *cost_matrix_obj;
  int verbose = 0;
  static const char *kwlist[] = {"cost_matrix", "verbose", NULL};
  if (!PyArg_ParseTupleAndKeywords(
      args, kwargs, "O|p", const_cast<char**>(kwlist),
      &cost_matrix_obj, &verbose)) {
    return NULL;
  }

  // Ensure array view; do not cast dtype.
  pyarray cost_matrix_array(PyArray_FROM_OTF(
      cost_matrix_obj, NPY_NOTYPE, NPY_ARRAY_IN_ARRAY));
  if (!cost_matrix_array) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\" must be a numpy array");
    return NULL;
  }
  int typ = PyArray_TYPE(cost_matrix_array.get());
  if (typ != NPY_FLOAT32 && typ != NPY_FLOAT64) {
    PyErr_SetString(PyExc_TypeError, "\"cost_matrix\" must be float32 or float64 for lapjvs_native()");
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
  if (dim <= 0) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\"'s shape is invalid or too large");
    return NULL;
  }

  auto cost_matrix = PyArray_DATA(cost_matrix_array.get());

  npy_intp ret_dims[] = {dim, 0};
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

// Float32 entry point: lapjvs_float32(cost_matrix, verbose=False)
// - Casts to float32 if needed, but avoids a copy when already float32.
// - Returns (row_ind, col_ind).
static PyObject *py_lapjvs_float32(PyObject *self, PyObject *args, PyObject *kwargs) {
  PyObject *cost_matrix_obj;
  int verbose = 0;
  static const char *kwlist[] = {"cost_matrix", "verbose", NULL};
  if (!PyArg_ParseTupleAndKeywords(
      args, kwargs, "O|p", const_cast<char**>(kwlist),
      &cost_matrix_obj, &verbose)) {
    return NULL;
  }

  // Allow casting to float32, avoid copy if dtype already matches.
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
  if (dim <= 0) {
    PyErr_SetString(PyExc_ValueError, "\"cost_matrix\"'s shape is invalid or too large");
    return NULL;
  }

  auto cost_matrix = PyArray_DATA(cost_matrix_array.get());

  npy_intp ret_dims[] = {dim, 0};
  pyarray row_ind_array(PyArray_SimpleNew(1, ret_dims, NPY_INT));
  pyarray col_ind_array(PyArray_SimpleNew(1, ret_dims, NPY_INT));
  auto row_ind = reinterpret_cast<int*>(PyArray_DATA(row_ind_array.get()));
  auto col_ind = reinterpret_cast<int*>(PyArray_DATA(col_ind_array.get()));

  std::unique_ptr<float[]> v(new float[dim]);
  call_lap<float>(dim, cost_matrix, verbose, row_ind, col_ind, v.get());

  return Py_BuildValue("(OO)", row_ind_array.get(), col_ind_array.get());
}