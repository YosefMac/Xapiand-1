import math
import requests
import json
import os


# Author: Michael Woods
# Home Page: https://github.com/vgm64/gmplot
# Keywords: python wrapper google maps
# License: MIT
# Package Index Owner: Michael.Woods


class GoogleMapPlotter(object):

	def __init__(self, center_lat, center_lng, zoom):
		self.center = (float(center_lat), float(center_lng))
		self.zoom = int(zoom)
		self.grids = None
		self.paths = []
		self.shapes = []
		self.points = []
		self.heatmap_points = []
		self.radpoints = []
		self.gridsetting = None

	@classmethod
	def from_geocode(cls, location_string, zoom=13):
		lat, lng = cls.geocode(location_string)
		return cls(lat, lng, zoom)

	@classmethod
	def geocode(self, location_string):
		geocode = requests.get(
			'http://maps.googleapis.com/maps/api/geocode/json?address="%s"' % location_string)
		geocode = json.loads(geocode.text)
		latlng_dict = geocode['results'][0]['geometry']['location']
		return latlng_dict['lat'], latlng_dict['lng']

	def grid(self, slat, elat, latin, slng, elng, lngin):
		self.gridsetting = [slat, elat, latin, slng, elng, lngin]

	def marker(self, lat, lng, color='#00FF00', c='#00FF00', title="no implementation"):
		self.points.append((lat, lng, color, title))

	def scatter(self, lats, lngs, color=None, size=None, marker=True, c=None, s=None, **kwargs):
		color = color or c
		size = size or s or 40
		kwargs["color"] = color
		kwargs["size"] = size
		settings = self._process_kwargs(kwargs)
		for lat, lng in zip(lats, lngs):
			if marker:
				self.marker(lat, lng, settings['color'])
			else:
				self.circle(lat, lng, size, **settings)

	def circle(self, lat, lng, radius, color=None, c=None, **kwargs):
		color = color or c
		kwargs.setdefault('face_alpha', 0.2)
		kwargs.setdefault('face_color', "#000000")
		kwargs.setdefault("color", color)
		settings = self._process_kwargs(kwargs)
		path = self.get_cycle(lat, lng, radius)
		self.shapes.append((path, settings))

	def _process_kwargs(self, kwargs):
		settings = dict()
		settings["edge_color"] = kwargs.get("color", None) or \
								 kwargs.get("edge_color", None) or \
								 kwargs.get("ec", None) or \
								 "#000000"

		settings["edge_alpha"] = kwargs.get("alpha", None) or \
								 kwargs.get("edge_alpha", None) or \
								 kwargs.get("ea", None) or \
								 1.0
		settings["edge_width"] = kwargs.get("edge_width", None) or \
								 kwargs.get("ew", None) or \
								 1.0
		settings["face_alpha"] = kwargs.get("alpha", None) or \
								 kwargs.get("face_alpha", None) or \
								 kwargs.get("fa", None) or \
								 0.3
		settings["face_color"] = kwargs.get("color", None) or \
								 kwargs.get("face_color", None) or \
								 kwargs.get("fc", None) or \
								 "#000000"

		settings["color"] = kwargs.get("color", None) or \
							kwargs.get("c", None) or \
							settings["edge_color"] or \
							settings["face_color"]

		# Need to replace "plum" with "#DDA0DD" and "c" with "#00FFFF" (cyan).
		for key, color in settings.items():
			if 'color' in key:
				settings[key] = color

		settings["closed"] = kwargs.get("closed", None)

		return settings

	def plot(self, lats, lngs, color=None, c=None, **kwargs):
		color = color or c
		kwargs.setdefault("color", color)
		settings = self._process_kwargs(kwargs)
		path = zip(lats, lngs)
		self.paths.append((path, settings))

	def heatmap(self, lats, lngs, threshold=10, radius=10, gradient=None, opacity=0.6, dissipating=True):
		"""
		:param lats: list of latitudes
		:param lngs: list of longitudes
		:param threshold:
		:param radius: The hardest param. Example (string):
		:return:
		"""
		settings = {}
		settings['threshold'] = threshold
		settings['radius'] = radius
		settings['gradient'] = gradient
		settings['opacity'] = opacity
		settings['dissipating'] = dissipating
		settings = self._process_heatmap_kwargs(settings)

		heatmap_points = []
		for lat, lng in zip(lats, lngs):
			heatmap_points.append((lat, lng))
		self.heatmap_points.append((heatmap_points, settings))

	def _process_heatmap_kwargs(self, settings_dict):
		settings_string = ''
		settings_string += "heatmap.set('threshold', %d);\n" % settings_dict['threshold']
		settings_string += "heatmap.set('radius', %d);\n" % settings_dict['radius']
		settings_string += "heatmap.set('opacity', %f);\n" % settings_dict['opacity']

		dissipation_string = 'true' if settings_dict['dissipating'] else 'false'
		settings_string += "heatmap.set('dissipating', %s);\n" % (dissipation_string)

		gradient = settings_dict['gradient']
		if gradient:
			gradient_string = "var gradient = [\n"
			for r, g, b, a in gradient:
				gradient_string += "\t" + "'rgba(%d, %d, %d, %d)',\n" % (r, g, b, a)
			gradient_string += '];' + '\n'
			gradient_string += "heatmap.set('gradient', gradient);\n"

			settings_string += gradient_string

		return settings_string

	def polygon(self, lats, lngs, color=None, c=None, **kwargs):
		color = color or c
		kwargs.setdefault("color", color)
		settings = self._process_kwargs(kwargs)
		shape = zip(lats, lngs)
		self.shapes.append((shape, settings))

	# create the html file which include one google map and all points and
	# paths
	def draw(self, htmlfile):
		f = open(htmlfile, 'w')
		f.write('<html>\n')
		f.write('<head>\n')
		f.write(
			'<meta name="viewport" content="initial-scale=1.0, user-scalable=no" />\n')
		f.write(
			'<meta http-equiv="content-type" content="text/html; charset=UTF-8"/>\n')
		f.write('<title>Google Maps - pygmaps </title>\n')
		f.write('<script type="text/javascript" src="https://maps.googleapis.com/maps/api/js?libraries=visualization&sensor=true_or_false"></script>\n')
		f.write('<script type="text/javascript">\n')
		f.write('\tfunction initialize() {\n')
		self.write_map(f)
		self.write_grids(f)
		self.write_points(f)
		self.write_paths(f)
		self.write_shapes(f)
		self.write_heatmap(f)
		f.write('\t}\n')
		f.write('</script>\n')
		f.write('</head>\n')
		f.write(
			'<body style="margin:0px; padding:0px;" onload="initialize()">\n')
		f.write(
			'\t<div id="map_canvas" style="width: 100%; height: 100%;"></div>\n')
		f.write('</body>\n')
		f.write('</html>\n')
		f.close()

	#############################################
	# # # # # # Low level Map Drawing # # # # # #
	#############################################

	def write_grids(self, f):
		if self.gridsetting is None:
			return
		slat = self.gridsetting[0]
		elat = self.gridsetting[1]
		latin = self.gridsetting[2]
		slng = self.gridsetting[3]
		elng = self.gridsetting[4]
		lngin = self.gridsetting[5]
		self.grids = []

		r = [
			slat + float(x) * latin for x in range(0, int((elat - slat) / latin))]
		for lat in r:
			self.grids.append(
				[(lat + latin / 2.0, slng + lngin / 2.0), (lat + latin / 2.0, elng + lngin / 2.0)])

		r = [
			slng + float(x) * lngin for x in range(0, int((elng - slng) / lngin))]
		for lng in r:
			self.grids.append(
				[(slat + latin / 2.0, lng + lngin / 2.0), (elat + latin / 2.0, lng + lngin / 2.0)])

		for line in self.grids:
			settings = self._process_kwargs({"color": "#000000"})
			self.write_polyline(f, line, settings)

	def write_points(self, f):
		for point in self.points:
			self.write_point(f, point[0], point[1], point[2], point[3])

	def get_cycle(self, lat, lng, rad):
		# arcangle radius.
		cycle = []
		lat1 = (math.pi / 180.0) * lat
		lng1 = (math.pi / 180.0) * lng

		for a in range(360):
			tc = (math.pi / 180.0) * a
			y = math.asin(
				math.sin(lat1) * math.cos(rad) + math.cos(lat1) * math.sin(rad) * math.cos(tc))
			dlng = math.atan2(math.sin(
				tc) * math.sin(rad) * math.cos(lat1), math.cos(rad) - math.sin(lat1) * math.sin(y))
			x = ((lng1 - dlng + math.pi) % (2.0 * math.pi)) - math.pi
			cycle.append(
				(float(y * (180.0 / math.pi)), float(x * (180.0 / math.pi))))
		return cycle

	def write_paths(self, f):
		for path, settings in self.paths:
			self.write_polyline(f, path, settings)

	def write_shapes(self, f):
		for shape, settings in self.shapes:
			self.write_polygon(f, shape, settings)

	# TODO: Add support for mapTypeId: google.maps.MapTypeId.SATELLITE
	def write_map(self,  f):
		f.write('\t\tvar centerlatlng = new google.maps.LatLng(%f, %f);\n' %
				(self.center[0], self.center[1]))
		f.write('\t\tvar myOptions = {\n')
		f.write('\t\t\tzoom: %d,\n' % (self.zoom))
		f.write('\t\t\tcenter: centerlatlng,\n')
		f.write('\t\t\tmapTypeId: google.maps.MapTypeId.ROADMAP\n')
		f.write('\t\t};\n')
		f.write(
			'\t\tvar map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);\n')
		f.write('\n')

	def write_point(self, f, lat, lon, color, title):
		f.write('\t\tvar latlng = new google.maps.LatLng(%f, %f);\n' %
				(lat, lon))
		f.write('\t\tvar marker = new google.maps.Marker({\n')
		f.write('\t\ttitle: "%s",\n' % title)
		f.write('\t\tposition: latlng\n')
		f.write('\t\t});\n')
		f.write('\t\tmarker.setMap(map);\n')
		f.write('\n')

	def write_polyline(self, f, path, settings):
		clickable = False
		geodesic = True
		strokeColor = settings.get('color') or settings.get('edge_color')
		strokeOpacity = settings.get('edge_alpha')
		strokeWeight = settings.get('edge_width')

		f.write('var PolylineCoordinates = [\n')
		for coordinate in path:
			f.write('new google.maps.LatLng(%f, %f),\n' %
					(coordinate[0], coordinate[1]))
		f.write('];\n')
		f.write('\n')

		f.write('var Path = new google.maps.Polyline({\n')
		f.write('clickable: %s,\n' % (str(clickable).lower()))
		f.write('geodesic: %s,\n' % (str(geodesic).lower()))
		f.write('path: PolylineCoordinates,\n')
		f.write('strokeColor: "%s",\n' % (strokeColor))
		f.write('strokeOpacity: %f,\n' % (strokeOpacity))
		f.write('strokeWeight: %d\n' % (strokeWeight))
		f.write('});\n')
		f.write('\n')
		f.write('Path.setMap(map);\n')
		f.write('\n\n')

	def write_polygon(self, f, path, settings):
		clickable = False
		geodesic = True
		strokeColor = settings.get('edge_color') or settings.get('color')
		strokeOpacity = settings.get('edge_alpha')
		strokeWeight = settings.get('edge_width')
		fillColor = settings.get('face_color') or settings.get('color')
		fillOpacity= settings.get('face_alpha')
		f.write('var coords = [\n')
		for coordinate in path:
			f.write('new google.maps.LatLng(%f, %f),\n' %
					(coordinate[0], coordinate[1]))
		f.write('];\n')
		f.write('\n')

		f.write('var polygon = new google.maps.Polygon({\n')
		f.write('clickable: %s,\n' % (str(clickable).lower()))
		f.write('geodesic: %s,\n' % (str(geodesic).lower()))
		f.write('fillColor: "%s",\n' % (fillColor))
		f.write('fillOpacity: %f,\n' % (fillOpacity))
		f.write('paths: coords,\n')
		f.write('strokeColor: "%s",\n' % (strokeColor))
		f.write('strokeOpacity: %f,\n' % (strokeOpacity))
		f.write('strokeWeight: %d\n' % (strokeWeight))
		f.write('});\n')
		f.write('\n')
		f.write('polygon.setMap(map);\n')
		f.write('\n\n')

	def write_heatmap(self, f):
		for heatmap_points, settings_string in self.heatmap_points:
			f.write('var heatmap_points = [\n')
			for heatmap_lat, heatmap_lng in heatmap_points:
				f.write('new google.maps.LatLng(%f, %f),\n' %
						(heatmap_lat, heatmap_lng))
			f.write('];\n')
			f.write('\n')
			f.write('var pointArray = new google.maps.MVCArray(heatmap_points);' + '\n')
			f.write('var heatmap;' + '\n')
			f.write('heatmap = new google.maps.visualization.HeatmapLayer({' + '\n')
			f.write('\n')
			f.write('data: pointArray' + '\n')
			f.write('});' + '\n')
			f.write('heatmap.setMap(map);' + '\n')
			f.write(settings_string)
