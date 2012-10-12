import unittest
import dbc
import math


class Test(unittest.TestCase):
    def testAssignmentViolation(self):
        class X(dbc._Dbc):
            """
            inv: self.bla > 5
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
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
        class X(dbc._Dbc):
            """
            inv: self.bla > 5
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 0
        with self.assertRaises(dbc.DbcViolation):
            x = X()  # @UnusedVariable

    def testInitOk(self):
        class X(dbc._Dbc):
            """
            inv: self.bla > 5
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 10
                self.bla = 15
                self.bla = 6
        x = X()  # @UnusedVariable

    def testInvariantsParsed(self):
        class X(dbc._Dbc):
            """
            teststring
            inv: self.bla > 5 \
                 and self.bla< 15
            some explanation for the invariant maybe
            inv: self.bla > 7
            more docs
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 10
        x = X()
        self.assertEqual(len(x.__invariants__), 2)

    def testNoInvariants(self):
        class X(dbc._Dbc):
            """
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 10
        x = X()
        x.bla = 0
        x.bla = 20

    def testNoDocString(self):
        class X(dbc._Dbc):
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 10
        x = X()
        x.bla = 0
        x.bla = 20

    def testFunctionViolation(self):
        class X(dbc._Dbc):
            """
            inv: self.bla > 5
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 10

            def violate(self):
                self.bla = -1

        x = X()
        with self.assertRaises(dbc.DbcViolation):
            x.violate()

    def testFunctionViolationByUser(self):
        class X(dbc._Dbc):
            """
            inv: self.bla > 5
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
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
        class X(dbc._Dbc):
            """
            inv: self.bla > 5
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 10

        x = X()
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 5
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 5
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 5

    def testSimplePostViolation(self):
        class X(dbc._Dbc):
            def __init__(self):
                dbc._Dbc.__init__(self)
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
        class X(dbc._Dbc):
            def __init__(self):
                dbc._Dbc.__init__(self)
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
        class X(dbc._Dbc):
            def __init__(self):
                dbc._Dbc.__init__(self)
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
        class X(dbc._Dbc):
            def __init__(self):
                dbc._Dbc.__init__(self)
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
        class X(dbc._Dbc):
            def __init__(self):
                dbc._Dbc.__init__(self)
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
        class X(dbc._Dbc):
            def __init__(self):
                """
                pre: self.bla < 5
                """
                dbc._Dbc.__init__(self)
                self.bla = 10

        with self.assertRaises(AttributeError):
            x = X()  # @UnusedVariable

    def testPostInInit(self):
        class X(dbc._Dbc):
            def __init__(self):
                """
                post: self.bla < 5
                """
                dbc._Dbc.__init__(self)
                self.bla = 10

        with self.assertRaises(AttributeError):
            x = X()  # @UnusedVariable

    def testInheritance(self):
        class X(dbc._Dbc):
            """
            inv: self.bla < 15
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 10

            def change(self, value):
                self.bla = 15

        class Y(X):
            """
            inv: self.blabla < 20
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
        class X(dbc._Dbc, object):
            """
            inv: self.bla > 5
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
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
        class X(dbc._Dbc, object):
            """
            inv: self.bla > 5
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 0
        with self.assertRaises(dbc.DbcViolation):
            x = X()  # @UnusedVariable

    def testNewStyleInitOk(self):
        class X(dbc._Dbc, object):
            """
            inv: self.bla > 5
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 10
                self.bla = 15
                self.bla = 6
        x = X()  # @UnusedVariable

    def testNewStyleInvariantsParsed(self):
        class X(dbc._Dbc, object):
            """
            teststring
            inv: self.bla > 5 \
                 and self.bla< 15
            some explanation for the invariant maybe
            inv: self.bla > 7
            more docs
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 10
        x = X()
        self.assertEqual(len(x.__invariants__), 2)

    def testNewStyleNoInvariants(self):
        class X(dbc._Dbc, object):
            """
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 10
        x = X()
        x.bla = 0
        x.bla = 20

    def testNewStyleNoDocString(self):
        class X(dbc._Dbc, object):
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 10
        x = X()
        x.bla = 0
        x.bla = 20

    def testNewStyleFunctionViolation(self):
        class X(dbc._Dbc, object):
            """
            inv: self.bla > 5
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 10

            def violate(self):
                self.bla = -1

        x = X()
        with self.assertRaises(dbc.DbcViolation):
            x.violate()

    def testNewStyleFunctionViolationByUser(self):
        class X(dbc._Dbc, object):
            """
            inv: self.bla > 5
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
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
        class X(dbc._Dbc, object):
            """
            inv: self.bla > 5
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 10

        x = X()
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 5
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 5
        with self.assertRaises(dbc.DbcViolation):
            x.bla = 5

    def testNewStyleSimplePostViolation(self):
        class X(dbc._Dbc, object):
            def __init__(self):
                dbc._Dbc.__init__(self)
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
        class X(dbc._Dbc, object):
            def __init__(self):
                dbc._Dbc.__init__(self)
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
        class X(dbc._Dbc, object):
            def __init__(self):
                dbc._Dbc.__init__(self)
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
        class X(dbc._Dbc, object):
            def __init__(self):
                dbc._Dbc.__init__(self)
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
        class X(dbc._Dbc, object):
            def __init__(self):
                dbc._Dbc.__init__(self)
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
        class X(dbc._Dbc, object):
            def __init__(self):
                """
                pre: self.bla < 5
                """
                dbc._Dbc.__init__(self)
                self.bla = 10

        with self.assertRaises(AttributeError):
            x = X()  # @UnusedVariable

    def testNewStylePostInInit(self):
        class X(dbc._Dbc, object):
            def __init__(self):
                """
                post: self.bla < 5
                """
                dbc._Dbc.__init__(self)
                self.bla = 10

        with self.assertRaises(AttributeError):
            x = X()  # @UnusedVariable

    def testNewStyleInheritance(self):
        class X(dbc._Dbc, object):
            """
            inv: self.bla < 15
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 10

            def change(self, value):
                self.bla = 15

        class Y(X):
            """
            inv: self.blabla < 20
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
        class X(dbc._Dbc, object):
            """
            inv: self.bla < 15
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 10

            def change(self, value):
                self.bla = 15

        class Y(X):
            """
            inv: self.bla < 12
            """
            pass

        y = Y()
        self.assertEqual(len(y.__invariants__), 2)
        with self.assertRaises(dbc.DbcViolation):
            y.change(20)
        with self.assertRaises(dbc.DbcViolation):
            y.change(12)

    def testNewStyleInheritance3(self):
        class X(dbc._Dbc, object):
            """
            inv: self.bla < 15
            """
            def __init__(self):
                dbc._Dbc.__init__(self)
                self.bla = 10

        class Y(X):
            """
            inv: self.bla < 10
            """
            pass

        x = X()  # @UnusedVariable
        with self.assertRaises(dbc.DbcViolation):
            y = Y()  # @UnusedVariable

    def testComplexPost(self):
        class X(dbc._Dbc, object):
            def __init__(self):
                dbc._Dbc.__init__(self)
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
        class X(dbc._Dbc, object):
            def __init__(self):
                dbc._Dbc.__init__(self)

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
        class X(dbc._Dbc, object):
            def __init__(self):
                dbc._Dbc.__init__(self)
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
        class X(dbc._Dbc, object):
            def __init__(self):
                dbc._Dbc.__init__(self)
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
        @dbc._dbc_function_wrapper
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

            @dbc._dbc_function_wrapper
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


if __name__ == "__main__":
    unittest.main()
