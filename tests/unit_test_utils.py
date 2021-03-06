import doctest
from unittest import TestCase

import pandas as pd
import xarray as xr

from . import test_utils


class TestUtils(TestCase):

    def test_xrsplit(self):
        import pysd

        array1d = xr.DataArray([0.5, 0., 1.],
                               {'ABC': ['A', 'B', 'C']},
                               ['ABC'])
        array2d = xr.DataArray([[0.5, -1.5],
                                [-1., -0.5],
                                [-0.75, 0.]],
                                {'ABC': ['A', 'B', 'C'],
                                 'XY': ['X', 'Y']},
                                ['ABC', 'XY'])
        array3d = xr.DataArray([[[0.5, 4.] , [-1.5, 3.]],
                                [[-1., 2.], [-0.5, 5.5]],
                                [[-0.75, 0.75], [0., -1.]]],
                                {'ABC': ['A', 'B', 'C'],
                                 'XY': ['X', 'Y'],
                                 'FG': ['F', 'G']},
                                ['ABC', 'XY', 'FG'])
        s1d = pysd.utils.xrsplit(array1d)
        s2d = pysd.utils.xrsplit(array2d)
        s3d = pysd.utils.xrsplit(array3d)

        # check length
        self.assertEqual(len(s1d), 3)
        self.assertEqual(len(s2d), 6)
        self.assertEqual(len(s3d), 12)

        # check all values for 1d
        self.assertIn(xr.DataArray(0.5, {'ABC': ['A']}, ['ABC']), s1d)
        self.assertIn(xr.DataArray(0., {'ABC': ['B']}, ['ABC']), s1d)
        self.assertIn(xr.DataArray(1., {'ABC': ['C']}, ['ABC']), s1d)
        # check some values for 2d and 3d
        self.assertIn(xr.DataArray(0.5,
                                   {'ABC': ['A'],'XY': ['X']},
                                   ['ABC', 'XY']),
                      s2d)
        self.assertIn(xr.DataArray(-0.5,
                                   {'ABC': ['B'],'XY': ['Y']},
                                   ['ABC', 'XY']),
                      s2d)
        self.assertIn(xr.DataArray(-0.5,
                                   {'ABC': ['B'],'XY': ['Y'], 'FG': ['F']},
                                   ['ABC', 'XY', 'FG']),
                      s3d)
        self.assertIn(xr.DataArray(0.75,
                                   {'ABC': ['C'],'XY': ['X'], 'FG': ['G']},
                                   ['ABC', 'XY', 'FG']),
                      s3d)

    def test_get_return_elements_subscirpts(self):
        import pysd

        self.assertEqual(
            pysd.utils.get_return_elements(["Inflow A[Entry 1,Column 1]",
                                 "Inflow A[Entry 1,Column 2]"],
                                {'Inflow A': 'inflow_a'},
                                {'Dim1': ['Entry 1', 'Entry 2'],
                                 'Dim2': ['Column 1', 'Column 2']}),
            (['inflow_a'],
             {'Inflow A[Entry 1,Column 1]': ('inflow_a', ('Entry 1', 'Column 1')),
              'Inflow A[Entry 1,Column 2]': ('inflow_a', ('Entry 1', 'Column 2'))}
             )
        )

    def test_get_return_elements_realnames(self):
        import pysd
        self.assertEqual(
            pysd.utils.get_return_elements(["Inflow A",
                                 "Inflow B"],
                                subscript_dict={'Dim1': ['Entry 1', 'Entry 2'],
                                                'Dim2': ['Column 1', 'Column 2']},
                                namespace={'Inflow A': 'inflow_a',
                                           'Inflow B': 'inflow_b'}),
            (['inflow_a', 'inflow_b'],
             {'Inflow A': ('inflow_a', None),
              'Inflow B': ('inflow_b', None)}
             )
        )

    def test_get_return_elements_pysafe_names(self):
        import pysd
        self.assertEqual(
            pysd.utils.get_return_elements(["inflow_a",
                                 "inflow_b"],
                                subscript_dict={'Dim1': ['Entry 1', 'Entry 2'],
                                                'Dim2': ['Column 1', 'Column 2']},
                                namespace={'Inflow A': 'inflow_a',
                                           'Inflow B': 'inflow_b'}),
            (['inflow_a', 'inflow_b'],
             {'inflow_a': ('inflow_a', None),
              'inflow_b': ('inflow_b', None)}
             )
        )

    def test_get_return_elements_not_found_error(self):
        """"
        Test for not found element
        """
        import pysd

        with self.assertRaises(KeyError):
            pysd.utils.get_return_elements([
                "inflow_a",
                "inflow_b", "inflow_c"],
                subscript_dict={'Dim1': ['Entry 1', 'Entry 2'],
                                'Dim2': ['Column 1', 'Column 2']},
                namespace={'Inflow A': 'inflow_a',
                           'Inflow B': 'inflow_b'})

    def test_make_flat_df(self):
        import pysd

        frames = [{'elem1': xr.DataArray([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                                       {'Dim1': ['A', 'B', 'C'],
                                        'Dim2': ['D', 'E', 'F']},
                                       dims=['Dim1', 'Dim2']),
                   'elem2': xr.DataArray([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                                       {'Dim1': ['A', 'B', 'C'],
                                        'Dim2': ['D', 'E', 'F']},
                                       dims=['Dim1', 'Dim2'])},
                  {'elem1': xr.DataArray([[2, 4, 6], [8, 10, 12], [14, 16, 19]],
                                         {'Dim1': ['A', 'B', 'C'],
                                          'Dim2': ['D', 'E', 'F']},
                                       dims=['Dim1', 'Dim2']),
                   'elem2': xr.DataArray([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                                         {'Dim1': ['A', 'B', 'C'],
                                          'Dim2': ['D', 'E', 'F']},
                                       dims=['Dim1', 'Dim2'])}]

        return_addresses = {'Elem1[B,F]': ('elem1', {'Dim1': ['B'], 'Dim2': ['F']})}
        df = pd.DataFrame([{'Elem1[B,F]': 6}, {'Elem1[B,F]': 12}])
        resultdf = pysd.utils.make_flat_df(frames, return_addresses)

        test_utils.assert_frames_close(resultdf, df, rtol=.01)

    def test_visit_addresses(self):
        import pysd

        frame = {'elem1': xr.DataArray([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                                       {'Dim1': ['A', 'B', 'C'],
                                        'Dim2': ['D', 'E', 'F']},
                                       dims=['Dim1', 'Dim2']),
                 'elem2': xr.DataArray([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                                       {'Dim1': ['A', 'B', 'C'],
                                        'Dim2': ['D', 'E', 'F']},
                                       dims=['Dim1', 'Dim2'])}

        return_addresses = {'Elem1[B,F]': ('elem1', {'Dim1': ['B'], 'Dim2': ['F']})}
        self.assertEqual(pysd.utils.visit_addresses(frame, return_addresses),
                         {'Elem1[B,F]': 6})

    def test_visit_addresses_nosubs(self):
        import pysd

        frame = {'elem1': 25, 'elem2': 13}
        return_addresses = {'Elem1': ('elem1', {}),
                            'Elem2': ('elem2', {})}

        self.assertEqual(pysd.utils.visit_addresses(frame, return_addresses),
                         {'Elem1': 25, 'Elem2': 13})

    def test_visit_addresses_return_array(self):
        """ There could be cases where we want to
        return a whole section of an array - ie, by passing in only part of
        the simulation dictionary. in this case, we can't force to float..."""
        import pysd

        frame = {'elem1': xr.DataArray([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                                       {'Dim1': ['A', 'B', 'C'],
                                        'Dim2': ['D', 'E', 'F']},
                                       dims=['Dim1', 'Dim2']),
                 'elem2': xr.DataArray([[1, 2, 3], [4, 5, 6], [7, 8, 9]],
                                       {'Dim1': ['A', 'B', 'C'],
                                        'Dim2': ['D', 'E', 'F']},
                                        dims=['Dim1', 'Dim2'])}
        return_addresses = {'Elem1[A, Dim2]': ('elem1', {'Dim1': ['A'], 'Dim2': ['D', 'E', 'F']})}

        actual = pysd.utils.visit_addresses(frame, return_addresses)
        expected = {'Elem1[A, Dim2]':
                        xr.DataArray([[1, 2, 3]],
                                     {'Dim1': ['A'],
                                      'Dim2': ['D', 'E', 'F']},
                                     dims=['Dim1', 'Dim2']),
                    }
        self.assertIsInstance(list(actual.values())[0], xr.DataArray)
        self.assertEqual(actual['Elem1[A, Dim2]'].shape,
                         expected['Elem1[A, Dim2]'].shape)
        # Todo: test that the values are equal

    def test_make_coord_dict(self):
        import pysd
        self.assertEqual(pysd.utils.make_coord_dict(['Dim1', 'D'],
                                         {'Dim1': ['A', 'B', 'C'],
                                          'Dim2': ['D', 'E', 'F']},
                                         terse=True),
                         {'Dim2': ['D']})
        self.assertEqual(pysd.utils.make_coord_dict(['Dim1', 'D'],
                                         {'Dim1': ['A', 'B', 'C'],
                                          'Dim2': ['D', 'E', 'F']},
                                         terse=False),
                         {'Dim1': ['A', 'B', 'C'], 'Dim2': ['D']})

    def test_find_subscript_name(self):
        import pysd
        self.assertEqual(pysd.utils.find_subscript_name({'Dim1': ['A', 'B'],
                                              'Dim2': ['C', 'D', 'E'],
                                              'Dim3': ['F', 'G', 'H', 'I']},
                                             'D'),
                         'Dim2')

        self.assertEqual(pysd.utils.find_subscript_name({'Dim1': ['A', 'B'],
                                              'Dim2': ['C', 'D', 'E'],
                                              'Dim3': ['F', 'G', 'H', 'I']},
                                             'Dim3'),
                         'Dim3')

    def test_doctests(self):
        import pysd
        doctest.DocTestSuite(pysd.utils)

    def test_make_merge_list(self):
        from warnings import catch_warnings
        from pysd.py_backend.utils import make_merge_list

        subscript_dict = {
            "layers": ["l1", "l2", "l3"],
            "layers1": ["l1", "l2", "l3"],
            "up": ["l2", "l3"],
            "down": ["l1", "l2"],
            "dim": ["A", "B", "C"],
            "dim1": ["A", "B", "C"]
        }

        self.assertEqual(
            make_merge_list([["l1"],["up"]],
                            subscript_dict),
            ["layers"])

        self.assertEqual(
            make_merge_list([["l3", "dim1"],["down", "dim1"]],
                            subscript_dict),
            ["layers", "dim1"])

        self.assertEqual(
            make_merge_list([["l2", "dim1", "dim"],["l1", "dim1", "dim"]],
                            subscript_dict),
           ["down", "dim1", "dim"])

        self.assertEqual(
            make_merge_list([["layers1", "l2"],["layers1", "l3"]],
                            subscript_dict),
           ["layers1", "up"])

        # incomplete dimension
        with catch_warnings(record=True) as ws:
            self.assertEqual(
                make_merge_list([["A"],["B"]],
                                subscript_dict),
                ["dim"])
            # use only user warnings
            wu = [w for w in ws if issubclass(w.category, UserWarning)]
            self.assertTrue(len(wu), 1)
            self.assertIn("Dimension given by subscripts:"
                          + "\n\t{}\nis incomplete ".format({"A", "B"})
                          + "using {} instead.".format("dim")
                          + "\nSubscript_dict:"
                          + "\n\t{}".format(subscript_dict),
                          str(wu[0].message))

        # invalid dimension
        try:
            make_merge_list([["l1"],["B"]],
                            subscript_dict)
            self.assertFail()
        except ValueError as err:
            self.assertIn("Impossible to find the dimension that contains:"
                          + "\n\t{}\nFor subscript_dict:".format({"l1","B"})
                          + "\n\t{}".format(subscript_dict),
                          err.args[0])

    def test_compute_shape(self):
        """"
        Test for computing the shape of an array giving coordinates dictionary
        and ordered dimensions.
        """
        from pysd.py_backend.utils import compute_shape

        coords = [
          {},
          {'ABC': ['A', 'B', 'C'],
           'XY': ['X'],
           'val': [1, 2, 3, 4, 5, 6, 7, 8]},
          {'val': [1, 2, 3, 4, 5],
           'ABC': ['A', 'B', 'C'],
           'XY': ['X']},
          {'ABC': ['A', 'B', 'C'],
           'val': [1, 2, 3, 4, 5, 6, 7, 8],
           'XY': ['X', 'Y']},
          {'val': [1, 2, 3, 4, 5, 6, 7, 8],
           'ABC': ['A', 'B', 'C']},
          {'val': [1, 2, 3, 4, 5, 6, 7, 8]}
         ]

        shapes = [[], [3, 1, 8], [5, 3, 1], [3, 8, 2], [8, 3], [8]]

        for c, s in zip(coords, shapes):
            self.assertEqual(compute_shape(c), s)

    def test_compute_shape_reshape(self):
        """"
        Test for computing the shape of an array giving coordinates dictionary
        and ordered dimensions with reshape.
        """
        from pysd.py_backend.utils import compute_shape

        coords = [
          {'ABC': ['A', 'B', 'C'],
           'XY': ['X'],
           'val': [1, 2, 3, 4, 5, 6, 7, 8]},
          {'val': [1, 2, 3, 4, 5],
           'ABC': ['A', 'B', 'C'],
           'XY': ['X']},
          {'ABC': ['A', 'B', 'C'],
           'val': [1, 2, 3, 4, 5, 6, 7, 8],
           'XY': ['X', 'Y']},
          {'val': [1, 2, 3, 4, 5, 6, 7, 8],
           'ABC': ['A', 'B', 'C']},
          {'val': [1, 2, 3, 4, 5, 6, 7, 8]}
         ]

        # reshapes list for 1, 2 and 3
        shapes123 = [
          [None, None, None, None, [8]],
          [[3, 8], [5, 3], None, [8, 3], [1, 8]],
          [[1, 3, 8], [1, 5, 3], [3, 8, 2], [1, 8, 3], [1, 1, 8]]
        ]

        for i, shapes in enumerate(shapes123):
            for c, s in zip(coords, shapes):
                if s:
                    self.assertEqual(compute_shape(c, i+1), s)
                else:
                    with self.assertRaises(ValueError):
                        compute_shape(c, i+1)

    def test_rearrange(self):
        from pysd.py_backend.utils import rearrange

        # simple cases are tested, complex cases are tested with test-models
        _subscript_dict = {
            'd1': ['a', 'b', 'c'],
            'd2': ['b', 'c'],
            'd3': ['b', 'c']
        }

        xr_input_subdim = xr.DataArray([1, 4, 2],
            {'d1': ['a', 'b', 'c']}, ['d1'])
        xr_input_updim = xr.DataArray([1, 4],
            {'d2': ['b', 'c']}, ['d2'])
        xr_input_switch = xr.DataArray([[1, 4],[8, 5]],
            {'d2': ['b', 'c'], 'd3': ['b', 'c']}, ['d2', 'd3'])
        xr_input_float = 3.

        xr_out_subdim = xr.DataArray([4, 2],
            {'d2': ['b', 'c']}, ['d2'])
        xr_out_updim = xr.DataArray([[1, 1], [4, 4]],
            {'d2': ['b', 'c'], 'd3': ['b', 'c']}, ['d2', 'd3'])
        xr_out_switch = xr.DataArray([[1, 4],[8, 5]],
            {'d2': ['b', 'c'], 'd3': ['b', 'c']}, ['d3', 'd2'])
        xr_out_float = xr.DataArray(3.,
            {'d2': ['b', 'c']}, ['d2'])

        self.assertTrue(xr_out_subdim.equals(
            rearrange(xr_input_subdim, ['d2'], _subscript_dict)))

        self.assertTrue(xr_out_updim.equals(
            rearrange(xr_input_updim, ['d2', 'd3'], _subscript_dict)))

        self.assertTrue(xr_out_switch.equals(
            rearrange(xr_input_switch, ['d3', 'd2'], _subscript_dict)))

        self.assertTrue(xr_out_float.equals(
            rearrange(xr_input_float, ['d2'], _subscript_dict)))

        self.assertEqual(None,
            rearrange(None, ['d2'], _subscript_dict))

    def test_round_(self):
        import pysd
        coords = {'d1': [9, 1], 'd2': [2, 4]}
        dims = ['d1', 'd2']
        xr_input = xr.DataArray([[1.2, 2.7], [3.05, 4]], coords, dims)
        xr_output = xr.DataArray([[1., 3.], [3., 4.]], coords, dims)

        self.assertEqual(pysd.utils.round_(2.7), 3)
        self.assertEqual(pysd.utils.round_(4.2), 4)
        self.assertTrue(pysd.utils.round_(xr_input).equals(xr_output))

    def test_add_entries_underscore(self):
        """"
        Test for add_entries_undescore
        """
        from pysd.py_backend.utils import add_entries_underscore

        dict1 = {'CD': 10, 'L F': 5}
        dict2 = {'a b': 1, 'C': 2, 'L M H': 4}

        dict1b = dict1.copy()

        add_entries_underscore(dict1b)

        self.assertTrue('L_F' in dict1b)
        self.assertEqual(dict1b['L F'], dict1b['L_F'])

        add_entries_underscore(dict1, dict2)

        self.assertTrue('L_F' in dict1)
        self.assertEqual(dict1['L F'], dict1['L_F'])
        self.assertTrue('a_b' in dict2)
        self.assertEqual(dict2['a b'], dict2['a_b'])
        self.assertTrue('L_M_H' in dict2)
        self.assertEqual(dict2['L M H'], dict2['L_M_H'])

    def test_make_add_identifier(self):
        """
        Test make_add_identifier for the .add methods py_name
        """
        from pysd.py_backend.utils import make_add_identifier

        build_names = set()

        name = "values"
        build_names.add(name)

        self.assertEqual(make_add_identifier(name, build_names), "valuesADD_1")
        self.assertEqual(make_add_identifier(name, build_names), "valuesADD_2")
        self.assertEqual(make_add_identifier(name, build_names), "valuesADD_3")

        name2 = "bb_a"
        build_names.add(name2)
        self.assertEqual(make_add_identifier(name2, build_names), "bb_aADD_1")
        self.assertEqual(make_add_identifier(name, build_names), "valuesADD_4")
        self.assertEqual(make_add_identifier(name2, build_names), "bb_aADD_2")


    def test_progressbar(self):
        import pysd

        pbar = pysd.py_backend.utils.ProgressBar(10)

        for i in range(10):
            self.assertEqual(pbar.counter, i)
            pbar.update()

        pbar.finish()

        pbar = pysd.py_backend.utils.ProgressBar()
        self.assertFalse(hasattr(pbar, 'counter'))
        pbar.update()
        pbar.finish()
