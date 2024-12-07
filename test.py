import unittest
import sys
from io import StringIO
from mainn import lex, parse, interpret, Token # Import your functions

class TestConfigTranslator(unittest.TestCase):

    def test_lex_simple(self):
        input_text = "name1 := value1\nname2 := 123"
        tokens = lex(input_text)
        self.assertEqual(len(tokens), 6)
        self.assertEqual(tokens[0].value, "name1")
        self.assertEqual(tokens[1].value, ":=")
        self.assertEqual(tokens[2].value, "value1")
        self.assertEqual(tokens[3].value, "name2")
        self.assertEqual(tokens[4].value, ":=")
        self.assertEqual(tokens[5].value, "123")

    def test_lex_string(self):
        input_text = "name := q(This is a string)"
        tokens = lex(input_text)
        self.assertEqual(len(tokens), 3)
        self.assertEqual(tokens[2].value, "This is a string")

    def test_lex_error(self):
        input_text = "invalid line"
        tokens = lex(input_text)
        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].type, Token.ERROR)

    def test_parse_simple(self):
        tokens = [
            Token(Token.NAME, "name1"), Token(Token.ASSIGN, ":="), Token(Token.STRING, "value1"),
            Token(Token.NAME, "name2"), Token(Token.ASSIGN, ":="), Token(Token.NUMBER, "123")
        ]
        constants = parse(tokens)
        self.assertEqual(constants["name1"], "value1")
        self.assertEqual(constants["name2"], "123")

    def test_parse_array(self):
        tokens = [
            Token(Token.NAME, "names"), Token(Token.ASSIGN, ":="), Token(Token.ARRAY_START, "{"),
            Token(Token.STRING, "nameA"), Token(Token.STRING, "nameB"), Token(Token.STRING, "nameC"),
            Token(Token.ARRAY_END, "}")
        ]
        constants = parse(tokens)
        self.assertEqual(constants["names"], ["nameA", "nameB", "nameC"])

    def test_parse_error(self):
        tokens = [Token(Token.NAME, "name1"), Token(Token.ASSIGN, ":="), Token(Token.ERROR, "invalid")]
        with self.assertRaises(ValueError):
            parse(tokens)

    def test_interpret_variable_substitution(self):
        constants = {"name1": "value1", "name2": "$name1"}
        interpreted = interpret(constants)
        self.assertEqual(interpreted["name2"], "value1")

    def test_interpret_nested_substitution(self):
        constants = {"name1": "value1", "name2": "$name1", "name3": "$name2"}
        interpreted = interpret(constants)
        self.assertEqual(interpreted["name3"], "value1")

    def test_interpret_undefined_variable(self):
        constants = {"name1": "value1", "name2": "$name3"}
        with self.assertRaises(ValueError):
            interpret(constants)



if __name__ == '__main__':
    unittest.main()
