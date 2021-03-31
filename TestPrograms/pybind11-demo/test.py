import example


def test_add():
    assert add(2, 3) == 5


def test_pet():
    my_dog = Pet('Pluto', 5)
    assert my_dog.get_name() == 'Pluto'
    assert my_dog.get_hunger() == 5
    my_dog.go_for_a_walk()
    assert my_dog.get_hunger() == 6
    
def taint(x):
    return x

a = 1
b = 2
a = taint(a)
b = taint(b)

example.add(a, b)

print(example)  # have to do it like this because of some bug

my_dog = example.Pet('Pluto', 5)
print(my_dog.get_name())
print(my_dog.get_hunger())

my_dog.go_for_a_walk()
print(my_dog.get_hunger())



