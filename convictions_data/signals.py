import django.dispatch

pre_geocode_page = django.dispatch.Signal(providing_args=["page_num", "num_pages"])

post_geocode_page = django.dispatch.Signal(providing_args=["page_number", "num_pages"])

post_load_spatial_data = django.dispatch.Signal(providing_args=["model"])


