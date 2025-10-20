#include <functional>
#include <memory>
#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <numpy/arrayobject.h>
#include "lapjvs.h"

static char module_docstring[] =
    "This module wraps LAPJVS - Jonker-Volgenant linear sum assignment algorithm (Scalar-only, no AVX2/SIMD).";
static char lapjvs_docstring[] =
    "Solves the linear sum assignment problem (Scalar-only).";

static PyObject *py_lapjvs(PyObject *self, PyObject *args, PyObject *kwargs);

static PyMethodDef module_functions[] = {
  {"lapjvs", reinterpret_cast<PyCFunction>(py_lapjvs),
   METH_VARARGS | METH_KEYWORDS, lapjvs_docstring},
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
static always_inline double call_lap(int dim, const void *restrict cost_matrix,
                                     bool verbose,
                                     int *restrict row_ind, int *restrict col_ind,
                                     void *restrict u, void *restrict v) {
  double lapcost;
  Py_BEGIN_ALLOW_THREADS
  auto cost_matrix_typed = reinterpret_cast<const F*>(cost_matrix);
  auto u_typed = reinterpret_cast<F*>(u);
  auto v_typed = reinterpret_cast<F*>(v);
  if (verbose) {
    lapcost = lapjvs<true>(dim, cost_matrix_typed, row_ind, col_ind, u_typed, v_typed);
  } else {
    lapcost = lapjvs<false>(dim, cost_matrix_typed, row_ind, col_ind, u_typed, v_typed);
  }
  Py_END_ALLOW_THREADS
  return lapcost;
}

static PyObject *py_lapjvs(PyObject *self, PyObject *args, PyObject *kwargs) {
  PyObject *cost_matrix_obj;
  int verbose = 0;
  int force_doubles = 0;
  int return_original = 0;
  static const char *kwlist[] = {
      "cost_matrix", "verbose", "force_doubles", "return_original", NULL};
  if (!PyArg_ParseTupleAndKeywords(
      args, kwargs, "O|pbb", const_cast<char**>(kwlist),
      &cost_matrix_obj, &verbose, &force_doubles, &return_original)) {
    return NULL;
  }

  // Restore fast default: process as float32 unless force_doubles is set.
  pyarray cost_matrix_array;
  bool float32 = true;
  cost_matrix_array.reset(PyArray_FROM_OTF(
      cost_matrix_obj, NPY_FLOAT32,
      NPY_ARRAY_IN_ARRAY | (force_doubles ? 0 : NPY_ARRAY_FORCECAST)));
  if (!cost_matrix_array) {
    PyErr_Clear();
    float32 = false;
    cost_matrix_array.reset(PyArray_FROM_OTF(
        cost_matrix_obj, NPY_FLOAT64, NPY_ARRAY_IN_ARRAY));
    if (!cost_matrix_array) {
      PyErr_SetString(PyExc_ValueError, "\"cost_matrix\" must be a numpy array of float32 or float64 dtype");
      return NULL;
    }
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

  double lapcost;

  if (return_original) {
    // Allocate NumPy arrays for u, v only if they are returned.
    pyarray u_array(PyArray_SimpleNew(
        1, ret_dims, float32? NPY_FLOAT32 : NPY_FLOAT64));
    pyarray v_array(PyArray_SimpleNew(
        1, ret_dims, float32? NPY_FLOAT32 : NPY_FLOAT64));
    auto u = PyArray_DATA(u_array.get());
    auto v = PyArray_DATA(v_array.get());
    if (float32) {
      lapcost = call_lap<float>(dim, cost_matrix, verbose, row_ind, col_ind, u, v);
    } else {
      lapcost = call_lap<double>(dim, cost_matrix, verbose, row_ind, col_ind, u, v);
    }
    return Py_BuildValue("(OO(dOO))",
                         row_ind_array.get(), col_ind_array.get(), lapcost,
                         u_array.get(), v_array.get());
  } else {
    // Temporary heap buffers for u, v to avoid NumPy allocation overhead.
    if (float32) {
      std::unique_ptr<float[]> u(new float[dim]);
      std::unique_ptr<float[]> v(new float[dim]);
      lapcost = call_lap<float>(dim, cost_matrix, verbose, row_ind, col_ind, u.get(), v.get());
    } else {
      std::unique_ptr<double[]> u(new double[dim]);
      std::unique_ptr<double[]> v(new double[dim]);
      lapcost = call_lap<double>(dim, cost_matrix, verbose, row_ind, col_ind, u.get(), v.get());
    }
    return Py_BuildValue("(dOO)", lapcost, row_ind_array.get(), col_ind_array.get());
  }
}