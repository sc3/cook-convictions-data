from django.db.models import Q

# Categories of crimes, from IUCR codes
#
# These are based on CPD IUCR Codes on the City’s website:  
# CPD IUCR Codes on the City’s website:  
# https://data.cityofchicago.org/Public-Safety/Chicago-Police-Department-Illinois-Uniform-Crime-R/c7ck-438e

homicide_iucr_codes = ('0110', '0130', '0141', '0142')
homicide_nonindex_iucr_codes = ('0141', '0142')

sexual_assault_iucr_codes = ('0261', '0263', '0264', '0265',
    '0266', '0271', '0272', '0273', '0274', '0275', '0281', '0291')

robbery_iucr_codes = ('0312', '0313', '0320', '0325', '0326',
    '0330', '0331', '0334', '0337', '0340', '031A', '031B', '033A',
    '033B')

agg_assault_iucr_codes = ('0520', '0530', '0550', '0551', '0552',
    '0553', '0554', '0555', '0556', '0557', '0558', '051A', '051B')
agg_assault_nonindex_iucr_codes = ('0554',)
# The following are types of assault but don't seem to be aggrevated:
# 0545: "PRO EMP HANDS NO/MIN INJURY"
# 0560: "SIMPLE" 
non_agg_assault_iucr_codes = ('0545', '0560')

agg_battery_iucr_codes = ('0420', '0430', '0440', '0450', '0451', '0452',
    '0453', '0454', '0461', '0462', '0479', '0480', '0481', '0482', '0483',
    '0485', '0487', '0488', '0489', '0495', '0496', '0497', '0498',
    '041A', '041B')
agg_battery_nonindex_iucr_codes = ('0440', '0454', '0487')
non_agg_battery_iucr_codes = ('0460', '0475', '0484', '0486')

burglary_iucr_codes = ('0610', '0620', '0630', '0650')

theft_iucr_codes = ('0810', '0820', '0840', '0841', '0842', '0843', '0850',
    '0860', '0865', '0870', '0880', '0890', '0895')

motor_vehicle_theft_iucr_codes = ('0910', '0915', '0917', '0918', '0920',
    '0925', '0927', '0928', '0930', '0935', '0937', '0938')

arson_iucr_codes = ('1010', '1020', '1025', '1030', '1035', '1090')
arson_nonindex_iucr_codes = ('1030', '1035')

# These aren't part of a category as defined as CPD.  We're grouping them
# ourselves.
# As such the battery charges get counted in the Agg battery / agg assault
# category and also get counted in the domestic violence category for the
# purposes of our project.  We will not displaying these numbers together so
# it should not be a problem.
domestic_violence_iucr_codes = ('0486', '0488', '0489', '0496', '0497',
    '0498')

stalking_iucr_codes = ('0580', '0581', '0583')

violating_order_protection_iucr_codes = ('4387')

crimes_affecting_women_iucr_codes = list(sexual_assault_iucr_codes) + list(domestic_violence_iucr_codes) + list(violating_order_protection_iucr_codes)


drug_iucr_codes = ('1811', '1812', '1821', '1822', '1840', '1850', '1860',
    '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018',
    '2019', '2020', '2021', '2022', '2023', '2024', '2025', '2026', '2027',
    '2028', '2029', '2030', '2031', '2032', '2040', '2050', '2060', '2070',
    '2080', '2090', '2091', '2092', '2093', '2094', '2095', '2110', '2111',
    '2120', '2160', '2170')

# Q objects that will be used in the call to filter()

homicide_iucr_query = Q(iucr_code__in=homicide_iucr_codes)
homicide_nonindex_iucr_query = Q(iucr_code__in=homicide_nonindex_iucr_codes)
sexual_assault_iucr_query = Q(iucr_code__in=sexual_assault_iucr_codes)
robbery_iucr_query = Q(iucr_code__in=robbery_iucr_codes)
agg_assault_iucr_query = Q(iucr_code__in=agg_assault_iucr_codes)
agg_assault_nonindex_iucr_query = Q(iucr_code__in=agg_assault_iucr_codes)
non_agg_assault_iucr_query = Q(iucr_code__in=non_agg_assault_iucr_codes) 
agg_battery_iucr_query = Q(iucr_code__in=agg_battery_iucr_codes)
agg_battery_nonindex_iucr_query = Q(iucr_code__in=agg_battery_nonindex_iucr_codes)
burglary_iucr_query = Q(iucr_code__in=burglary_iucr_codes)
theft_iucr_query = Q(iucr_code__in=theft_iucr_codes)
motor_vehicle_theft_iucr_query = Q(iucr_code__in=motor_vehicle_theft_iucr_codes)
arson_iucr_query = Q(iucr_code__in=arson_iucr_codes)
arson_nonindex_iucr_query = Q(iucr_code__in=arson_nonindex_iucr_codes)
domestic_violence_iucr_query = Q(iucr_code__in=domestic_violence_iucr_codes)
stalking_iucr_query = Q(iucr_code__in=stalking_iucr_codes)
violating_order_protection_iucr_query = Q(iucr_code__in=crimes_affecting_women_iucr_codes)

drug_iucr_query = Q(iucr_code__in=drug_iucr_codes)

violent_iucr_query = (homicide_iucr_query | sexual_assault_iucr_query |
    robbery_iucr_query | agg_battery_iucr_query |
    agg_assault_iucr_query)

violent_nonindex_iucr_query = (homicide_nonindex_iucr_query |
        agg_assault_nonindex_iucr_query |
        agg_battery_nonindex_iucr_query)

property_iucr_query = (burglary_iucr_query | theft_iucr_query |
        motor_vehicle_theft_iucr_query | arson_iucr_query)

crimes_affecting_women_iucr_query = (sexual_assault_iucr_query |
    domestic_violence_iucr_query |
    violating_order_protection_iucr_query)

