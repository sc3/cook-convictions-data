"""
Queries for types of convictions based on ILCS statute references.

This is needed to try to categorize records with statutes that don't
map to an IUCR code.  In many cases this is because the mapping is
genuinely ambiguous.  The statute defines acts which could map to multiple
crimes as defined in the IUCR list.
"""
from django.db.models import Q

CRIMINAL_SEXUAL_ASSAULT_STATUTE_QUERY = Q(final_statute_formatted__istartswith='720-5/12-14')

# IUCR 0261
AGGREVATED_CRIMINAL_SEXUAL_ASSAULT_STATUTE_QUERY = Q(final_statute_formatted__istartswith='720-5/12-16(')

PROPERTY_INDEX_STATUTE_QUERY = (
    # Motor vehicle theft
    Q(final_statute_formatted__istartswith='625-5/4-103(a)') |

    # Theft
    Q(final_statute_formatted__istartswith='720-5/16-1') |

    # Deceptive practice or bad checks
    # IUCR 1110
    Q(final_statute_formatted__istartswith='720-5/17-1(B)') |

    # Burglary
    # IUCR 0610
    Q(final_statute_formatted__istartswith='720-5/19-1') |

    # Aggravated Discharge of a Firearm
    # IUCR 1415
    Q(final_statute_formatted__istartswith='720-5/24-1.2')
)

NONVIOLENT_INDEX_STATUTE_QUERY = PROPERTY_INDEX_STATUTE_QUERY

NONVIOLENT_STATUTE_QUERY = NONVIOLENT_INDEX_STATUTE_QUERY | (
    # Animal fighting
    Q(final_statute_formatted__istartswith='510-70/4.01(a)') |

    # Dog fighting
    # ILCS 720-5/26-5
    # This section was renumbered as section 48-1
    # These map to both IUCR 1685 (Dog or Animal Fighting for Gambling Purposes)
    # and 2885 (Dog or Animal Fighting for Entertainment)
    # but it's hard to disambiguate these based on charge description.
    # However, these are both nonindex offenses
    Q(final_statute_formatted__istartswith='720-5/26-5') |

    # DUI
    Q(final_statute_formatted__istartswith='625-5/11-501') |

    # Harassing phone calls
    Q(final_statute_formatted__istartswith='720-135/1') |

    # TODO: Are these violent or nonviolent?
    # Involuntary Manslaughter and Reckless Homicide
    # ILCS 720-5/9-3
    # IUCR 0141 (Involuntary Manslaughter) and IUCR 0142 (Reckless Homicide)
    # The charge descriptions don't disambiguate between these two crimes.
    Q(final_statute_formatted__istartswith='720-5/9-3')
)

VIOLENT_INDEX_STATUTE_QUERY = (
    CRIMINAL_SEXUAL_ASSAULT_STATUTE_QUERY |
    AGGREVATED_CRIMINAL_SEXUAL_ASSAULT_STATUTE_QUERY
)

VIOLENT_STATUTE_QUERY = VIOLENT_INDEX_STATUTE_QUERY 

AFFECTING_WOMEN_STATUTE_QUERY = (
    CRIMINAL_SEXUAL_ASSAULT_STATUTE_QUERY |
    AGGREVATED_CRIMINAL_SEXUAL_ASSAULT_STATUTE_QUERY
)
