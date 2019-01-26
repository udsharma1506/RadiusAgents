# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.


class User(models.Models):
	'''
	User models to save the basic user details
	'''

	name = models.CharField(max_length=255)
	contact_info = models.CharField(max_length=255)
	mail_id = models.CharField(max_length=255)

class Search(models.Models):
	'''
	Search models to save the data of the requirements entered by the user
	'''
	# user who is entering the requirement
	user = models.ForeignKey(User, blank = True)

	date_added = models.DateTimeField(auto_now=True)
	
	city = models.CharField(max_length=1000)				# city name ( used in first level filtering )
	country = models.CharField(max_length=1000)				# country	
	# all the basic params getting from the user for search
	latitude = models.DecimalField(max_digits=12,decimal_places=8)
	longitude = models.DecimalField(max_digits=12,decimal_places=8)
	min_budget = models.IntegerField(default=0)
	max_budget = models.IntegerField(default=0)
	min_bedrooms = models.IntegerField(default = 0)
	max_bedrooms = models.IntegerField(default = 0)
	min_bathrooms = models.IntegerField(default = 0)
	max_bathrooms = models.IntegerField(default = 0)

	def serializer(self):
		'''
		Serializer to get the Dict data of the Search instance
		'''

		data = {}

		data['user'] = self.user.id
		data['location'] = {"latitude": self.latitude,"longitude": self.longitude}
		data['min_budget'] = self.min_budget 
		data['max_budget'] = self.max_budget
		data['min_bedrooms'] = self.min_bedrooms
		data['max_bedrooms'] = self.max_bedrooms
		data['min_bathrooms'] = self.min_bathrooms
		data['max_bathrooms'] = self.max_bathrooms
		return data

class Property(models.Models):
	'''
	Property models to save the data entered for the property listing
	'''

	name = models.CharField(max_length=255)					# name of the property
	location = models.CharField(max_length=1000)			# full location address in text format
	descriptions = models.TextField(blank = True)			# description which user wants to give
	street = models.CharField(max_length=1000)				# street name of the proprty
	city = models.CharField(max_length=1000)				# city name ( used in filtering the properties)
	country = models.CharField(max_length=1000)				# country
	user = models.ForeignKey(User, blank = True)			# who is listing the property

	# basic details of the proprty 
	latitude = models.DecimalField(max_digits=12,decimal_places=8)	
	longitude = models.DecimalField(max_digits=12,decimal_places=8)
	price = models.IntegerField(default=0)
	number_of_bedrooms = models.IntegerField(default=0)
	number_of_bathrooms = models.IntegerField(default=0)

	def validate_distance(self, location):
		'''
		to calculate the distance between property and requirement and validate the radius for 10 km
		Input: property instance and location as dict containing latitude and longitude
		Output: Flag as True or False, distance between property and requirement
		'''
		import geopy.distance
		# get the coords for proprty and requirement
		coord_property = tuple(self.latitude, self.longitude) 
		coord_requirement = tuple(location.values())

		# calc distance using coords
		distance = geopy.distance.vincenty(coord_property, coord_requirement).km

		# Check if it is greated than 10 retuen False, else true
		if distance > 10:
			return False, distance
		else:
			return True, distance

	def calculate_percentage_validation(requirement_budget_max, property_price, percentage_range = .25, requirement_budget_min = None):
		'''
		to get the % match for the proprty price and budget given as requirement 
		Input:
		requirement_budget_max = max or min budget entered by the user
		property_price = price of the property
		percentage_range = to check the +/- % for the range
		requirement_budget_min = if min budget entered by user else None
		'''

		# set the uppper and lower value based on range
		percentage_range_upper_value = 1 + percentage_range
		percentage_range_lower_value = 1 - percentage_range

		# check min budget value
		if not requirement_budget_min:
			# if min budget is absent, make min and max both save since that is not going to change any values
			requirement_budget_min = requirement_budget_max

		# check the validation of the budget if falls in the range return True else False
		if requirement_budget_max * Decimal(percentage_range_upper_value) > property_price \
			or requirement_budget * Decimal(percentage_range_lower_value) < property_price:
		    return True
		else:
			return False

	def validate_budget(self, requirement):
		'''
		validate the budget as per condition
		Input : property instance and requirement data
		'''

		min_budget = requirement.get('min_budget')
		max_budget = requirement.get('max_budget')

		# if max and min both present
		if max_budget and min_budget:
			budget_flag = calculate_percentage_validation(max_budget, self.price, 0.25, min_budget) #range to evaluate 25 %

		# if max present and not min
		elif max_budget and not min_budget:
			budget_flag = calculate_percentage_validation(max_budget, self.price, 0.10) #range to evaluate 10%

		# if min present and not max
		elif not max_budget and min_budget:
			budget_flag = calculate_percentage_validation(min_budget, self.price, 0.10)#range to evaluate 10 %

		return budget_flag, .30 # return the flag and match % as 30

	def effective_matching( diff_max, diff_min = None):
		'''
		calculate the effective matching based on value 
		I supposed the formula to be matching percatage ( 20 here) / difference in the values of property and requirement
		output effective matching %
		'''

		if diff_min and diff_max > diff_min:
			return 0.2/diff_min
		else:
			return 0.2/diff_max

	def calculate_range_validation(max_bedrooms, min_bedrooms, property_bedrooms):
		'''
		validate the bedroom and bathroom proprty and requirement data and return result with % differences
		'''

		# get the difference
		difference_with_max = abs(max_bedrooms - property_bedrooms)

		# check if min or max bedrooms present, if not present default value 0 would be present
		# which will be treated as False in PYTHON
		if min_bedrooms:
			# if both present check the range fall and reply with the match % if true
			if max_bedrooms > property_bedrooms > min_bedrooms:
				return True, 0.2

			#  if not fall in range, check for the +/- 2 range for them and reply with effective matching % based on value
			difference_with_min = abs(min_bedrooms - property_bedrooms)
			if difference_with_max < 2 or difference_with_min < 2:
				return True, effective_matching(difference_with_max, difference_with_min)

		# if any one is absent check for the range and return effective matching % based on value
		elif abs(difference_with_max) < 2:
				return True, effective_matching(difference_with_max)
		else:
			return False, 0

	def validate_bedroom(self, requirement):
		'''
		validates the bedroom and bathroom data and return the match percentage
		'''

		min_bedrooms = requirement.get('min_bedrooms')
		max_bedrooms = requirement.get('max_bedrooms')

		# check the if both value present
		if min_bedrooms and max_bedrooms:
			bedroom_flag, match_percent = calculate_range_validation(max_bedrooms, min_bedrooms, self.number_of_bedrooms)

		# if max present and min is not present
		if not min_bedrooms and max_bedrooms:
			bedroom_flag, match_percent = calculate_range_validation(max_bedrooms, min_bedrooms, self.number_of_bedrooms)

		# if min present and max is not present
		if not max_bedrooms and min_bedrooms:
			bedroom_flag, match_percent = calculate_range_validation(min_bedrooms, max_bedrooms, self.number_of_bedrooms)


	def validate_property_with_requirement(self, requirement):
		'''
		calls the validation function for all the parameters
		returns the flag as True or False with the matching % if validated
		'''

		distance_flag, distance_value = self.validate_distance(self,requirement.get('location'))
		budget_flag, budget_percent_value = self.validate_budget(self, requirement)
		bedroom_flag, bedroom_match_percent = self.validate_bedroom(self, requirement)
		bathroom_flag, bathroom_match_percent = self.validate_bathroom(self, requirement)

		# if all the flags are True, then only property is selected to show to the user		
		if distance_flag and budget_flag and bedroom_flag and bathroom_flag:

			data = {
			'distance':distance_value,
			'budget':budget_percent_value,
			'bedroom':bedroom_match_percent,
			'bathroom':bathroom_match_percent
			}
			return True, data
		else:
			return False, {}
