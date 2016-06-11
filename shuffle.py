import random


def shuffle(people):
	targets = people[:]
	done = False
	while not done:
		random.shuffle(targets)
		done = all(people[i] != targets[i] for i in range(len(people)))
	return dict(zip(people, targets))



people = ["a", "b", "c", "d"]

relaciones = shuffle(people)

print(relaciones)

print(relaciones["a"])
