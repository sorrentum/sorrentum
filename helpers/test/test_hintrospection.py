import logging
import os
from typing import Any, Callable

import helpers.hdbg as hdbg
import helpers.hgit as hgit
import helpers.hintrospection as hintros
import helpers.hpickle as hpickle
import helpers.hstring as hstring
import helpers.hunit_test as hunitest

_LOG = logging.getLogger(__name__)


# #############################################################################
# Test_is_pickleable
# #############################################################################


def hello() -> bool:
    return False

class _ClassPickleable:
    """
    Class with pickleable param values.
    """

    def __init__(self) -> None:
        self._arg1 = 1
        self._arg2 = ["2", 3]

    @staticmethod
    def say2(self) -> None:
        print("Hello")

    def say(self) -> None:
        print("Hello")


class _ClassNonPickleable:
    """
    Class with non-pickleable param values.
    """

    def __init__(self) -> None:
        self._arg1 = lambda x: x
        self._arg2 = 2


class Test_is_pickleable1(hunitest.TestCase):
    def helper(
        self,
        obj: Any,
        exp_str: str,
        exp_bound: bool,
        exp_lambda: bool,
        exp_pickled: bool,
    ) -> None:
        _LOG.debug("obj=%s", obj)
        #
        act_str = str(obj)
        _LOG.debug("act_str=%s", act_str)
        _LOG.debug("exp_str=%s", exp_str)
        self.assert_equal(act_str, exp_str, purify_text=True)
        #
        act_bound = hintros.is_bound_to_object(obj)
        _LOG.debug("act_bound=%s", act_bound)
        _LOG.debug("exp_bound=%s", exp_bound)
        self.assertEqual(act_bound, exp_bound)
        #
        act_lambda = hintros.is_lambda_function(obj)
        _LOG.debug("act_lambda=%s", act_lambda)
        _LOG.debug("exp_lambda=%s", exp_lambda)
        self.assertEqual(act_lambda, exp_lambda)
        # Try to pickle.
        try:
            file_name = os.path.join(self.get_scratch_space(), "obj.pkl")
            hpickle.to_pickle(obj, file_name)
            act_pickled = True
        except AttributeError as e:
            _LOG.error("e=%s", e)
            act_pickled = False
        _LOG.debug("act_pickled=%s", act_pickled)
        _LOG.debug("exp_pickled=%s", exp_pickled)
        self.assertEqual(act_pickled, exp_pickled)
        
    def test_lambda1(self) -> None:
        # Local lambda.
        lambda_ = lambda: 0
        func = lambda_
        exp_str = (
            r"<function Test_is_pickleable1.test_lambda1.<locals>.<lambda> at 0x>"
        )
        # A lambda is not bound to an object.
        exp_bound = False
        exp_lambda = True
        # A lambda is not pickleable.
        exp_pickled = False
        self.helper(func, exp_str, exp_bound, exp_lambda, exp_pickled)

    def test_lambda2(self) -> None:
        lambda_ = lambda x: x
        func = lambda_
        exp_str = (
            r"<function Test_is_pickleable1.test_lambda2.<locals>.<lambda> at 0x>"
        )
        # A lambda is not bound to an object.
        exp_bound = False
        exp_lambda = True
        # A lambda is not pickleable.
        exp_pickled = False
        self.helper(func, exp_str, exp_bound, exp_lambda, exp_pickled)

    def test_func1(self) -> None:
        def _class_pickleable() -> bool:
            return False

        #
        func = _class_pickleable
        exp_str = (
            r"<function Test_is_pickleable1.test_func1.<locals>._hello at 0x>"
        )
        exp_bound = False
        exp_lambda = False
        # A local object is not pickleable.
        exp_pickled = False
        self.helper(func, exp_str, exp_bound, exp_lambda, exp_pickled)

    def test_func2(self) -> None:
        # Global function.
        func = hello
        exp_str = r"<function hello at 0x>"
        exp_bound = False
        exp_lambda = False
        # A global function is pickleable since it's not bound locally or
        # to an object.
        exp_pickled = True
        self.helper(func, exp_str, exp_bound, exp_lambda, exp_pickled)

    def test_method1(self) -> None:
        # A class method but unbound to an object.
        func = _ClassPickleable.say
        exp_str = r"<function Hello.say at 0x>"
        exp_bound = False
        exp_lambda = False
        # A unbound class method is actually pickleable.
        exp_pickled = True
        self.helper(func, exp_str, exp_bound, exp_lambda, exp_pickled)

    def test_method2(self) -> None:
        # A static class method.
        func = _ClassPickleable.say2
        exp_str = r"<function Hello.say2 at 0x>"
        exp_bound = False
        exp_lambda = False
        exp_pickled = True
        self.helper(func, exp_str, exp_bound, exp_lambda, exp_pickled)

    def test_method3(self) -> None:
        # A bound method.
        class_instance = _ClassPickleable()
        func = class_instance.say
        exp_str = r"<bound method Hello.say of <helpers.test.test_hintrospection.Hello object at 0x>>"
        exp_bound = True
        exp_lambda = False
        # A method bound to an object is just a function, so it's pickleable.
        exp_pickled = True
        self.helper(func, exp_str, exp_bound, exp_lambda, exp_pickled)

    def test_method4(self) -> None:
        # A static class method.
        class_instance = _ClassPickleable()
        func = class_instance.say2
        exp_str = r"<function Hello.say2 at 0x>"
        exp_bound = False
        exp_lambda = False
        exp_pickled = True
        self.helper(func, exp_str, exp_bound, exp_lambda, exp_pickled)


class Test_is_pickleable2(hunitest.TestCase):
    def helper(
        self,
        obj: Any,
        exp_pickled: bool,
    ) -> None:
        """
        Run the function and verify the outcome.
        """
        _LOG.debug("obj=%s", obj)
        act_pickled = hintros.is_pickleable(obj)
        _LOG.debug("act_pickled=%s", act_pickled)
        _LOG.debug("exp_pickled=%s", exp_pickled)
        self.assertEqual(act_pickled, exp_pickled)

    def test_non_callable1(self) -> None:
        """
        Check that a non-callable is pickleable.
        """
        obj = 1
        exp_pickled = True
        self.helper(obj, exp_pickled)

    def test_non_callable2(self) -> None:
        """
        Check that a non-callable Iterable is pickleable.
        """
        obj = [1, "2", 0.3]
        exp_pickled = True
        self.helper(obj, exp_pickled)

    def test_lambda1(self) -> None:
        """
        Check that a lambda function is not pickleable.
        """
        obj = lambda x: x
        exp_pickled = False
        self.helper(obj, exp_pickled)

    def test_func1(self) -> None:
        """
        Check that a local object is not pickleable. 
        """
        def _class_pickleable() -> bool:
            return False
        
        obj = _class_pickleable
        exp_pickled = True
        self.helper(obj, exp_pickled)

    def test_func2(self) -> None:
        """
        Check that a global object is pickleable. 
        """
        obj = hello
        exp_pickled = True
        self.helper(obj, exp_pickled)

    def test_method1(self) -> None:
        """
        Check that an unbound class method is pickleable. 
        """
        obj = _ClassPickleable.say
        exp_pickled = True
        self.helper(obj, exp_pickled)

    def test_method2(self) -> None:
        """
        Check that a static class method is pickleable. 
        """
        obj = _ClassPickleable.say2
        exp_pickled = True
        self.helper(obj, exp_pickled)

    def test_method3(self) -> None:
        """
        Check that a bound method is not pickleable. 
        """
        class_instance = _ClassPickleable()
        obj = class_instance.say
        exp_pickled = False
        self.helper(obj, exp_pickled)

    def test_method4(self) -> None:
        """
        Check that a static class method is pickleable. 
        """
        class_instance = _ClassPickleable()
        obj = class_instance.say2
        exp_pickled = True
        self.helper(obj, exp_pickled)

    def test_class1(self) -> None:
        """
        Check that a class with pickleable param values is considered pickleable.
        """
        obj = _ClassPickleable()
        exp_pickled = True
        self.helper(obj, exp_pickled)

    def test_class2(self) -> None:
        """
        Check that a class with not pickleable param values is considered pickleable.
        """
        obj = _ClassNonPickleable()
        exp_pickled = True
        self.helper(obj, exp_pickled)


# #############################################################################
# Test_get_function_name1
# #############################################################################


def test_function() -> None:
    pass


class Test_get_function_name1(hunitest.TestCase):
    def test1(self) -> None:
        act = hintros.get_function_name()
        exp = "test1"
        self.assert_equal(act, exp)


class Test_get_name_from_function1(hunitest.TestCase):
    def test1(self) -> None:
        act = hintros.get_name_from_function(test_function)
        act = hstring.remove_prefix(act, "amp.", assert_on_error=False)
        exp = "helpers.test.test_hintrospection.test_function"
        self.assert_equal(act, exp)


# #############################################################################
# Test_get_function_from_string1
# #############################################################################


def dummy_function() -> None:
    pass


class TestGetFunctionFromString1(hunitest.TestCase):
    def test1(self) -> None:
        """
        Test that function is correctly extracted from a string.
        """
        func_str = "helpers.test.test_hintrospection.dummy_function"
        # Compute the actual value.
        act_func = hintros.get_function_from_string(func_str)
        act = hintros.get_name_from_function(act_func)
        act = hstring.remove_prefix(act, "amp.", assert_on_error=False)
        # Compute the expected value.
        exp_func = dummy_function
        exp = hintros.get_name_from_function(exp_func)
        exp = hstring.remove_prefix(exp, "amp.", assert_on_error=False)
        # Run.
        hdbg.dassert_isinstance(act_func, Callable)
        self.assert_equal(act, exp)
