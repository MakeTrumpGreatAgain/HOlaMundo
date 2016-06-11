
import random

def _derange(people):
	derangement = people[:]
	done = False
	while not done:
		random.shuffle(derangement)
		done = all(people[i] != derangement[i] for i in range(len(people)))
	return derangement

class SecretSanta(object):
	def __init__(self, id):
		self.santa_id = id
		self.participants = []
		self.pairings = []
		self.is_open = True

	def sign_up(self, user):
		# If the user isn't already signed up, abort
		if any(user.id == participant.id for participant in self.participants):
			return False
		
		self.participants.append(user)
		return True

	def _get_full_name(self, user):
		return "{}{}{}".format(
			user.first_name,
			" " + user.last_name if user.last_name is not None else "",
			" (@" + user.username + ")" if user.username is not None else ""
		) 


	def user_list(self):
		return map(lambda p: self._get_full_name(p), self.participants)


	def get_secret_santa_for(self, user):
		for participant in self.participants:
			if participant.id == user.id:
				return self._get_full_name(self.pairings[participant])
		return None

	def close(self):
		if len(self.participants) < 2: return False

		self.is_open = False
		self.pairings = dict(zip(self.participants, _derange(self.participants)))
		return True

