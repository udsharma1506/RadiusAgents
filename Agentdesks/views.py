# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View
from .models import User, Search, Property
from .utils import *
# Create your views here.

# API class when user has entered the search
class GetPropertyfromRequirements(View):

	def get(self, request):

		# expect user id coming from the data params of GET request
		data = request.GET
		user = data.get("user")

		# get the requirements list of the user
		requirements_dict = get_user_requirements(user)

		# get the city and country using Google APU of the requirement
		city, country = get_city_country_from_requirements(requirements_dict.get('location'))

		# get the list of properties in the same city
		properties_list = Property.models.filter(city = city)

		# call for each property
		proprty_mapper = {}
		for proprty in properties_list:

			# validate the property data with requirements
			# if matched returns True with the mathcing data containing the % of matching
			validated, match_data = proprty.validate_property_with_requirement(requirements_dict)
			# if true check final aggregate else ignore this property
			if validated:
				# get the final aggregated % of match
				similarity = calculate_match_percentage(validation_data)
				# check if percentage is greater than 40%, save them else ignore
				if similarity > 0.4
					proprty_mapper[proprty.pk] = similarity

		# sort the results on the basis of descending order of matching percentage
		sorted_list = OrderedDict(sorted(proprty_mapper.items(), key= lambda k: k[1], reverse = True))
		return sorted_list

# API class when user has entered the property
class GetRequirementsfromProperty(View):

	def get(self, request):

		# expect user id coming from the data params of GET request
		data = request.GET
		user = data.get("property")

		# get proptery list
		proprty = Property.objects.get(pk = property_id)

		# get the city and country 
		location = {'latitude': proprty.latitude, longitude: proprty.longitude}
		city, country = get_city_country_from_requirements(location)

		# get all requirements for the same city
		requirements_list = Search.objects.filter(city = city)

		# call for each requirement
		requirement_mapper = {}
		for requirement in requirements_list:

			# get the serialized data
			requirements_dict = requirement.serialize()
			# validate each requirement with the property entered by the user
			validated, match_data = proprty.validate_property_with_requirement(requirements_dict)

			# if true check final aggregate else ignore this requirement
			if validated:
				# get the final aggregated % of match
				similarity = calculate_match_percentage(validation_data)
				# check if percentage is greater than 40%, save them else ignore
				if similarity > 0.4
					requirement_mapper[requirement.pk] = similarity

		# sort the results on the basis of descending order of matching percentage
		sorted_list = OrderedDict(sorted(requirement_mapper.items(), key= lambda k: k[1], reverse = True))
		return sorted_list




