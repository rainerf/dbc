import unittest
import dbc
import math


class Test(unittest.TestCase):
    def testAssignmentViolation(self):
        @dbc.dbc_class
        class X:
            """
            hinv: self.bla > 5
            """
            def __init__(self):
                self.bla = 10

        x = X()
        x.bla = 7
        x.bla = 6
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 5
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 4
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 3

    def testInitViolation(self):
        @dbc.dbc_class
        class X:
            """
            hinv: self.bla > 5
            """
            def __init__(self):
                self.bla = 0
        with self.assertRaises(dbc.DbcViolation):
            x = X()  # @UnusedVariable

    def testInitOk(self):
        @dbc.dbc_class
        class X:
            """
            hinv: self.bla > 5
            """
            def __init__(self):
                self.bla = 10
                self.bla = 15
                self.bla = 6
        x = X()  # @UnusedVariable

    def testInvariantsParsed(self):
        @dbc.dbc_class
        class X:
            """
            teststring
            hinv: self.bla > 5 \
                 and self.bla< 15
            some explanation for the invariant maybe
            hinv: self.bla > 7
            more docs
            """
            def __init__(self):
                self.bla = 10
        x = X()
        self.assertEqual(len(x.__invariants__), 2)

    def testNoInvariants(self):
        @dbc.dbc_class
        class X:
            """
            """
            def __init__(self):
                self.bla = 10
        x = X()
        x.bla = 0
        x.bla = 20

    def testNoDocString(self):
        @dbc.dbc_class
        class X:
            def __init__(self):
                self.bla = 10
        x = X()
        x.bla = 0
        x.bla = 20

    def testFunctionViolation(self):
        @dbc.dbc_class
        class X:
            """
            hinv: self.bla > 5
            """
            def __init__(self):
                self.bla = 10

            def violate(self):
                self.bla = -1

        x = X()
        with self.assertRaises(dbc.DbcViolation):
            x.violate()

    def testFunctionViolationByUser(self):
        @dbc.dbc_class
        class X:
            """
            hinv: self.bla > 5
            """
            def __init__(self):
                self.bla = 10

            def change(self, value):
                self.bla = 3 + value

        x = X()
        x.change(5)
        x.change(4)
        x.change(3)
        with self.assertRaises(dbc.DbcViolation):
            x.change(2)
        with self.assertRaises(dbc.DbcViolation):
            x.change(1)
        with self.assertRaises(dbc.DbcViolation):
            x.change(0)

    def testReassignViolation(self):
        @dbc.dbc_class
        class X:
            """
            hinv: self.bla > 5
            """
            def __init__(self):
                self.bla = 10

        x = X()
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 5
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 5
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 5

    def testSimplePostViolation(self):
        @dbc.dbc_class
        class X:
            def __init__(self):
                self.bla = 10

            def change(self, value):
                """
                post: self.bla < 5
                """
                self.bla = value

        x = X()
        with self.assertRaises(dbc.DbcViolation):
            x.change(5)

    def testPostOk(self):
        @dbc.dbc_class
        class X:
            def __init__(self):
                self.bla = 10

            def change(self, value):
                """
                post: self.bla < 5
                """
                self.bla = value

        x = X()
        x.change(4)
        x.change(3)
        x.change(2)
        x.change(1)

    def testPreOk(self):
        @dbc.dbc_class
        class X:
            def __init__(self):
                self.bla = 0

            def change(self, value):
                """
                pre: self.bla < 5
                """
                self.bla = value

        x = X()

        x.change(1)
        x.change(2)
        x.change(3)
        x.change(4)
        x.change(5)

    def testPreViolation(self):
        @dbc.dbc_class
        class X:
            def __init__(self):
                self.bla = 0

            def change(self, value):
                """
                pre: self.bla < 5
                """
                self.bla = value

        x = X()

        x.change(5)
        with self.assertRaises(dbc.DbcViolation):
            x.change(6)

    def testPreViolationByInit(self):
        @dbc.dbc_class
        class X:
            def __init__(self):
                self.bla = 10

            def change(self, value):
                """
                pre: self.bla < 5
                """
                self.bla = value

        x = X()
        with self.assertRaises(dbc.DbcViolation):
            x.change(4)

    def testPreInInit(self):
        @dbc.dbc_class
        class X:
            def __init__(self):
                """
                pre: self.bla < 5
                """
                self.bla = 10

        with self.assertRaises(AttributeError):
            x = X()  # @UnusedVariable

    def testPostInInit(self):
        @dbc.dbc_class
        class X:
            def __init__(self):
                """
                post: self.bla < 5
                """
                self.bla = 10

        with self.assertRaises(AttributeError):
            x = X()  # @UnusedVariable

    def testInheritance(self):
        @dbc.dbc_class
        class X:
            """
            hinv: self.bla < 15
            """
            def __init__(self):
                self.bla = 10

            def change(self, value):
                self.bla = 15

        class Y(X):
            """
            hinv: self.blabla < 20
            """
            def __init__(self):
                X.__init__(self)
                self.blabla = 10

            def change2(self, value):
                self.blabla = value

        y = Y()
        self.assertEqual(len(y.__invariants__), 2)
        with self.assertRaises(dbc.DbcViolation):
            y.change(20)
        with self.assertRaises(dbc.DbcViolation):
            y.change2(25)

    def testNewStyleAssignmentViolation(self):
        @dbc.dbc_class
        class X(object):
            """
            hinv: self.bla > 5
            """
            def __init__(self):
                self.bla = 10

        x = X()
        x.bla = 7
        x.bla = 6
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 5
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 4
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 3

    def testNewStyleInitViolation(self):
        @dbc.dbc_class
        class X(object):
            """
            hinv: self.bla > 5
            """
            def __init__(self):
                self.bla = 0
        with self.assertRaises(dbc.DbcViolation):
            x = X()  # @UnusedVariable

    def testNewStyleInitOk(self):
        @dbc.dbc_class
        class X(object):
            """
            hinv: self.bla > 5
            """
            def __init__(self):
                self.bla = 10
                self.bla = 15
                self.bla = 6
        x = X()  # @UnusedVariable

    def testNewStyleInvariantsParsed(self):
        @dbc.dbc_class
        class X(object):
            """
            teststring
            hinv: self.bla > 5 \
                 and self.bla< 15
            some explanation for the invariant maybe
            hinv: self.bla > 7
            more docs
            """
            def __init__(self):
                self.bla = 10
        x = X()
        self.assertEqual(len(x.__invariants__), 2)

    def testNewStyleNoInvariants(self):
        @dbc.dbc_class
        class X(object):
            """
            """
            def __init__(self):
                self.bla = 10
        x = X()
        x.bla = 0
        x.bla = 20

    def testNewStyleNoDocString(self):
        @dbc.dbc_class
        class X(object):
            def __init__(self):
                self.bla = 10
        x = X()
        x.bla = 0
        x.bla = 20

    def testNewStyleFunctionViolation(self):
        @dbc.dbc_class
        class X(object):
            """
            hinv: self.bla > 5
            """
            def __init__(self):
                self.bla = 10

            def violate(self):
                self.bla = -1

        x = X()
        with self.assertRaises(dbc.DbcViolation):
            x.violate()

    def testNewStyleFunctionViolationByUser(self):
        @dbc.dbc_class
        class X(object):
            """
            hinv: self.bla > 5
            """
            def __init__(self):
                self.bla = 10

            def change(self, value):
                self.bla = 3 + value

        x = X()
        x.change(5)
        x.change(4)
        x.change(3)
        with self.assertRaises(dbc.DbcViolation):
            x.change(2)
        with self.assertRaises(dbc.DbcViolation):
            x.change(1)
        with self.assertRaises(dbc.DbcViolation):
            x.change(0)

    def testNewStyleReassignViolation(self):
        @dbc.dbc_class
        class X(object):
            """
            hinv: self.bla > 5
            """
            def __init__(self):
                self.bla = 10

        x = X()
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 5
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 5
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 5

    def testNewStyleSimplePostViolation(self):
        @dbc.dbc_class
        class X(object):
            def __init__(self):
                self.bla = 10

            def change(self, value):
                """
                post: self.bla < 5
                """
                self.bla = value

        x = X()
        with self.assertRaises(dbc.DbcViolation):
            x.change(5)

    def testNewStylePostOk(self):
        @dbc.dbc_class
        class X(object):
            def __init__(self):
                self.bla = 10

            def change(self, value):
                """
                post: self.bla < 5
                """
                self.bla = value

        x = X()
        x.change(4)
        x.change(3)
        x.change(2)
        x.change(1)

    def testNewStylePreOk(self):
        @dbc.dbc_class
        class X(object):
            def __init__(self):
                self.bla = 0

            def change(self, value):
                """
                pre: self.bla < 5
                """
                self.bla = value

        x = X()

        x.change(1)
        x.change(2)
        x.change(3)
        x.change(4)
        x.change(5)

    def testNewStylePreViolation(self):
        @dbc.dbc_class
        class X(object):
            def __init__(self):
                self.bla = 0

            def change(self, value):
                """
                pre: self.bla < 5
                """
                self.bla = value

        x = X()

        x.change(5)
        with self.assertRaises(dbc.DbcViolation):
            x.change(6)

    def testNewStylePreViolationByInit(self):
        @dbc.dbc_class
        class X(object):
            def __init__(self):
                self.bla = 10

            def change(self, value):
                """
                pre: self.bla < 5
                """
                self.bla = value

        x = X()
        with self.assertRaises(dbc.DbcViolation):
            x.change(4)

    def testNewStylePreInInit(self):
        @dbc.dbc_class
        class X(object):
            def __init__(self):
                """
                pre: self.bla < 5
                """
                self.bla = 10

        with self.assertRaises(AttributeError):
            x = X()  # @UnusedVariable

    def testNewStylePostInInit(self):
        @dbc.dbc_class
        class X(object):
            def __init__(self):
                """
                post: self.bla < 5
                """
                self.bla = 10

        with self.assertRaises(AttributeError):
            x = X()  # @UnusedVariable

    def testNewStyleInheritance(self):
        @dbc.dbc_class
        class X(object):
            """
            hinv: self.bla < 15
            """
            def __init__(self):
                self.bla = 10

            def change(self, value):
                self.bla = 15

        class Y(X):
            """
            hinv: self.blabla < 20
            """
            def __init__(self):
                super(Y, self).__init__()
                self.blabla = 10

            def change2(self, value):
                self.blabla = value

        y = Y()
        self.assertEqual(len(y.__invariants__), 2)
        with self.assertRaises(dbc.DbcViolation):
            y.change(20)
        with self.assertRaises(dbc.DbcViolation):
            y.change2(25)

    def testNewStyleInheritance2(self):
        @dbc.dbc_class
        class X(object):
            """
            hinv: self.bla < 15
            """
            def __init__(self):
                self.bla = 10

            def change(self, value):
                self.bla = 15

        class Y(X):
            """
            hinv: self.bla < 12
            """
            pass

        y = Y()
        self.assertEqual(len(y.__invariants__), 2)
        with self.assertRaises(dbc.DbcViolation):
            y.change(20)
        with self.assertRaises(dbc.DbcViolation):
            y.change(12)

    def testNewStyleInheritance3(self):
        @dbc.dbc_class
        class X(object):
            """
            hinv: self.bla < 15
            """
            def __init__(self):
                self.bla = 10

        class Y(X):
            """
            hinv: self.bla < 10
            """
            pass

        x = X()  # @UnusedVariable
        with self.assertRaises(dbc.DbcViolation):
            y = Y()  # @UnusedVariable

    def testComplexPost(self):
        @dbc.dbc_class
        class X(object):
            def __init__(self):
                self.a = 0
                self.b = 0
                self.c = 0

            def calculate(self):
                """
                post: self.c*self.c == self.a*self.a + self.b*self.b
                """
                self.c = math.sqrt(math.pow(self.a, 2) + math.pow(self.b, 2))

        x = X()
        x.a = 3
        x.b = 4
        x.calculate()
        self.assertEqual(x.c, 5)

    def testPostFromParameters(self):
        @dbc.dbc_class
        class X(object):
            def calculate(self, a, b):
                """
                pre: a > 0
                pre: b > 0
                post: __ret__*__ret__ == a*a + b*b
                """
                return math.sqrt(math.pow(a, 2) + math.pow(b, 2))

        x = X()
        with self.assertRaises(dbc.DbcViolation):
            x.calculate(-1, 10)
        with self.assertRaises(dbc.DbcViolation):
            x.calculate(0, 10)
        with self.assertRaises(dbc.DbcViolation):
            x.calculate(10, -1)
        with self.assertRaises(dbc.DbcViolation):
            x.calculate(10, 0)

        self.assertEqual(x.calculate(3, 4), 5)

    def testPostFromParametersOk(self):
        @dbc.dbc_class
        class X(object):
            def __init__(self):
                self.c = 0

            def calculate(self, a, b):
                """
                post: self.c*self.c == a*a + b*b
                """
                self.c = math.sqrt(math.pow(a, 2) + math.pow(b, 2))

        x = X()
        x.calculate(3, 4)
        self.assertEqual(x.c, 5)

    def testPostFromParametersViolation(self):
        @dbc.dbc_class
        class X(object):
            def __init__(self):
                self.c = 0

            def calculate(self, a, b):
                """
                post: self.c*self.c == a*a + b*b
                """
                # sqrt is missing!
                self.c = math.pow(a, 2) + math.pow(b, 2)

        x = X()
        with self.assertRaises(dbc.DbcViolation):
            x.calculate(3, 4)
        self.assertEqual(x.c, 25)

    def testFunction(self):
        @dbc.dbc_function
        def calculate(a, b):
            """
            pre: a>0 and b>0
            post: __ret__*__ret__ == a*a + b*b
            """
            return math.sqrt(math.pow(a, 2) + math.pow(b, 2))

        self.assertEqual(calculate(3, 4), 5)
        self.assertEqual(calculate(5, 12), 13)
        self.assertEqual(calculate(15, 20), 25)

        with self.assertRaises(dbc.DbcViolation):
            calculate(-1, 10)
        with self.assertRaises(dbc.DbcViolation):
            calculate(0, 10)
        with self.assertRaises(dbc.DbcViolation):
            calculate(10, -1)
        with self.assertRaises(dbc.DbcViolation):
            calculate(10, 0)

    def testSingleMethod(self):
        class X:
            def __init__(self, a):
                self.a = a

            @dbc.dbc_function
            def calculate(self, b):
                """
                pre: b > 0
                post: __ret__*__ret__ == self.a*self.a + b*b
                """
                return math.sqrt(math.pow(self.a, 2) + math.pow(b, 2))

        x = X(3)
        self.assertEqual(x.calculate(4), 5)
        with self.assertRaises(dbc.DbcViolation):
            x.calculate(-1)
        with self.assertRaises(dbc.DbcViolation):
            x.calculate(0)

    def testSortOk(self):
        @dbc.dbc_function
        def mysort(a):
            """
            pre: len(a) >= 0
            post: all(__ret__[i] <= __ret__[i+1] for i in xrange(len(__ret__)-1))
            post: all(a.count(i) == __ret__.count(i) for i in set(a))
            post: len(__ret__) == len(a)
            post: id(__ret__) != id(a)
            """
            return sorted(a)

        self.assertEquals(mysort([4, 3, 1, 2, 1]), [1, 1, 2, 3, 4])

    def testSortViolation(self):
        @dbc.dbc_function
        def mysort(a):
            """
            pre: len(a) >= 0
            post: all(__ret__[i] <= __ret__[i+1] for i in xrange(len(__ret__)-1))
            post: all(a.count(i) == __ret__.count(i) for i in set(a))
            post: len(__ret__) == len(a)
            post: id(__ret__) != id(a)
            """
            return a

        with self.assertRaises(dbc.DbcViolation):
            mysort([4, 3, 1, 2, 1])

    def testSortInPlaceOk(self):
        @dbc.dbc_function
        def mysort(a):
            """
            pre: len(a) >= 0
            post: all(__ret__[i] <= __ret__[i+1] for i in xrange(len(__ret__)-1))
            post: all(__old__["a"].count(i) == __ret__.count(i) for i in set(__old__["a"]))
            post: len(__ret__) == len(__old__["a"])
            post: print(__old__["a"]) == None
            post: print(__ret__) == None
            post: id(__ret__) == id(a)
            """
            a.sort()
            return a

        self.assertEquals(mysort([4, 3, 1, 2, 1]), [1, 1, 2, 3, 4])

    def testSortInPlaceViolation(self):
        @dbc.dbc_function
        def mysort(a):
            """
            pre: len(a) >= 0
            post: all(__ret__[i] <= __ret__[i+1] for i in xrange(len(__ret__)-1))
            post: all(__old__["a"].count(i) == __ret__.count(i) for i in set(__old__["a"]))
            post: len(__ret__) == len(__old__["a"])
            post: print(__old__["a"]) == None
            post: print(__ret__) == None
            post: id(__ret__) == id(a)
            """
            return a

        with self.assertRaises(dbc.DbcViolation):
            mysort([4, 3, 1, 2, 1])

    def testSoftInvariantOk(self):
        @dbc.dbc_class
        class X:
            """
            sinv: self.x >= 0
            """
            def __init__(self):
                self.x = 10

            def change(self):
                self.x = -10
                self.x = 10

        x = X()
        x.change()

    def testSoftInvariantViolation(self):
        @dbc.dbc_class
        class X:
            """
            sinv: self.x >= 0
            """
            def __init__(self):
                self.x = 10

            def change(self):
                self.x = -10

        x = X()
        with self.assertRaises(dbc.DbcViolation):
            x.change()

    def testMethodCall1(self):
        @dbc.dbc_class
        class X:
            """
            hinv: self.check()
            """
            def __init__(self):
                self.x = 10

            def check(self):
                return self.x > 10

        with self.assertRaises(dbc.DbcViolation):
            x = X()  # @UnusedVariable

    def testMethodCall2(self):
        @dbc.dbc_class
        class X:
            """
            hinv: self.check()
            """
            def __init__(self):
                self.x = 15

            def check(self):
                return self.x > 10

        x = X()
        x.x = 11
        x.x = 12
        with self.assertRaises(dbc.DbcViolation):
            x.x = 10
        with self.assertRaises(dbc.DbcViolation):
            x.x = 9

if __name__ == "__main__":
    unittest.main()
