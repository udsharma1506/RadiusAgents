# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

# Create your tests here.


from .models import User, Search, Property


def get_user_requirements(user_id):
	'''
	takes user id and returns the list of requirements user has entered as of now 
	'''

	# filter the seach tables and getting the latest requirement entered by the user by ordering by date added
	search_filter = Search.objects.filter(user = user_id).order_by("-date_added").last()

	if search_filter:
		return search_filter.serializer()		# if requiremrnt is present, return the data
	else:
		raise Exception('No Requirements exist for the user')		# else raise an Exception


def get_city_country_from_requirements(location):

	#call to Google API to get the City, Country name from the lat and long
	location_data = call_google_maps_api(location)
	city = location_data.get('city')
	country = location_data.get('country')
	return city, country

def calculate_match_percentage(data):
	'''
	calculate the final match percentage between the property and requirements
	'''

	# intial value 0
	match_percentage = 0
	for key, value in data.items():

		if key == 'distance':
			# if distance between property and requirement is less than 2 km
			if value < 2:
				match_percentage = match_percentage + (.30*1.5) # add 30 % to the match percentage, 
																# weightage of 1.5 is added to distance
			else:
				# if greater than 2, add 30% divided by difference of distance to 10 Scale  
				match_percentage = match_percentage + (.30/(10 - value) *1.5)

		if key == 'budget':
			# add 30% match for the budget, with weightage 1.5
			match_percentage = match_percentage + (.30*1.5)

		if key == 'bedroom':
			# add the % with no weightage at all ( =1.0)
			match_percentage = match_percentage + value*1.0

		if key == 'bathroom':
			# add the % with no weightage at all ( =1.0)
			match_percentage = match_percentage + value*1.0

	# now normalise the result to get the weighted average
	match_percentage = match_percentage/(1.5+ 1.5+ 1.0 +1.0)

	return match_percentage