# Test that always succeeds because pytest exits with code 5 when there aren't any tests, causing CI to fail.
def test_egoboost():
	print("So true")
