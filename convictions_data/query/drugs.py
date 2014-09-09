from django.db.models import Q

# Queries for drug charges, based on charge descriptions

# Roughly, any drug charge that mentiones manufacture or delivery
mfg_delivery_chrgdesc_query = (Q(final_chrgdesc__icontains="MAN/DEL") |
    Q(final_chrgdesc__icontains="MANU/DEL") |
    Q(final_chrgdesc__icontains="POSS MANU") |
    Q(final_chrgdesc__icontains="MANUEL/DEL") |
    Q(final_chrgdesc__icontains="MFG/DEL") |
    Q(final_chrgdesc__icontains="MFG/DISTRIB") |
    Q(final_chrgdesc__icontains="MFG ") |
    Q(final_chrgdesc__iregex=r'DEL.*(CONT|SUB)') |
    # HACK: THe final '[^E]+' is to avoid a false positive of
    # "DELETE/FALSIFY TITLE DOCUMENT"
    Q(final_chrgdesc__iregex=r'^(AGG|ATT|ATTEMPT|CASUAL|EMP|METH|)[ \. ]*DEL[^E]+') |
    Q(final_chrgdesc__iregex=r'^(P[ \. ]*C[ \. ]*S[ \./]+|POSS(ES{1,2}(ION|)|)).*DEL'))

# Roughly, any drug charge that reflects possession
# We have to be careful with our regexes because the phrase "possession" is
# used frequently for descriptions of other types of crimes.
possession_chrgdesc_query = (Q(final_chrgdesc__iregex=r'POS{1,2}.*(CON|CTL|LOOK-ALIKE).*SUB') |
    Q(final_chrgdesc__iregex=r'POS{1,2}.*(CANN|COCA|METH|HERO|STEROID)') |
    Q(final_chrgdesc__iregex=r'POSS.*(GR|PILL|OBJECT)') |
    Q(final_chrgdesc__iregex=r'^POS{1,2}( OF| ) CAN(ABIS| )') |
    # ILCS 720-570/406(a), 720-570/406.2(a)
    Q(final_chrgdesc__icontains="SCRIPT") |
    # Ambiguous charge description.  We know this is a drug charge, and can
    # assume it's for possession based on the description, but we don't
    # know what drug it's for, or in what amount.
    Q(final_chrgdesc="ATTEMPT POSS/ MISDEMEANOR") |
    # Ambiguous charge descriptions.  To determine drug/amount, we'll need
    # to look at the statute for these.
    Q(final_chrgdesc__in=("POSS ANY SUB WITH INTENT", "POSSESION")) |
    Q(final_chrgdesc__iregex=r'POSS.* WITH INTENT TO DEL') |
    # Casual delivery of Cannibis, treat as possession based on statute
    # description
    Q(final_chrgdesc__iregex=r'CAS.* DEL')
)

drugs_in_penal_inst_chrgdesc_query = (Q(final_chrgdesc__iregex=r'(ATT(EMPT|)|).*(POSS|EMPDEL|BRING|BRG).*CANN([AI]BIS|).*PENAL') |
     Q(final_chrgdesc__iregex=r'(POSS(ES|)|EMP DEL|BRING|).*CON.*SUB.*PENAL'))

drug_paraphernalia_query = Q(final_chrgdesc__icontains="PARAPHER")

drug_trafficking_query = Q(final_chrgdesc__icontains="TRAFFIC")

cannabis_chrgdesc_query = Q(final_chrgdesc__icontains="CAN")
cannabis_statute_query = Q(final_chrgdesc__icontains="720-550")
cannabis_query = cannabis_chrgdesc_query | cannabis_statute_query

cannabis_mfg_delivery_chrgdesc_query = (mfg_delivery_chrgdesc_query &
    cannabis_query)
cannabis_possession_chrgdesc_query = (possession_chrgdesc_query &
    cannabis_query)
cannabis_chrgdesc_query = (cannabis_mfg_delivery_chrgdesc_query |
    cannabis_possession_chrgdesc_query)

# It's easier to just exclude the cannabis convictions to get the non-cannabis
# convictions rather than defining explicit queries

# After reviewing all the different charge descriptions, it's hard to reliably
# determine this level of granularity from the charge description.
# The statute's aren't consistently formatted, so we'll use regexes.

# Manufacture or Deliver or Possess with intent to Manufacture or Deliver

# Note:
# Charges that reflect attempted crimes are bumped down to lower
# classes of felonies or misdemeanors.  These often have
# ILCS 720-5/8-4 or ILRS 38-8-4 in the statute.
# Class X Felony -> Class 1 Felony
# Class 1 Felony -> Class 2 Felony
# Class 2 Felony -> Class 3 Felony
# Other Felony -> Class A Misdemeanor

# No drug, amount, class or amount specified
mfg_del_unkwn_query = Q(final_statute="720-570/407.1")
# These are in ILRS format.  The corresponding ILCS reference is
# 720-5/8-4, 720-570/401
mfg_del_att_unkwn_query = Q(final_statute__in=("38-8-4(1401 3)",
    "38-8-4/56.5-1401"))

# Class X Felony
# From http://www.criminallawyerillinois.com/2010/02/22/what-is-a-class-x-felony-in-illinois/:
# The Class X felony is, short of first degree murder, the most serious felony
# offense on the books in Illinois. Upon a finding of guilt, the court cannot
# sentence the defendant to probation. The offense has a mandatory minimum
# sentence of 6-30 years in the Department of Corrections.
# ILCS 720-570/401(a)

# Class X Felony, no amount specified
# ILCS 720-570/401(a)
mfg_del_unkwn_class_x_query = (Q(final_statute__iregex=r'720-570/401\(a\)\s*$') |
    Q(final_statute="56.5-1401-B"))

# Class X Felony, >= 15g, < 100g Heroin
# ILCS 720-570/401(a)(1)(A)
mfg_del_heroin_15_100_g_query = Q(final_statute__iregex=r'720-570/401\(a\)\(1\)\(a\)')

# Class X Felony, >= 100g, < 400 g Heroin
# ILCS 720-570/401(a)(1)(B)
mfg_del_heroin_100_400_g_query = Q(final_statute__iregex=r'720-570/401\(a\)\(1\)\(b\)')

# Class X Felony, >= 400g, < 900 g Heroin
# ILCS 720-570/401(a)(1)(C)
mfg_del_heroin_400_900_g_query = Q(final_statute__iregex=r'720-570/401\(a\)\(1\)\(c\)')

# Class X Felony, >= 900g Heroin
# ILCS 720-570/401(a)(1)(C)
mfg_del_heroin_gt_900_g_query = Q(final_statute__iregex=r'720-570/401\(a\)\(1\)\(d\)')

# Class X Felony, no amount specified Cocaine
# ILCS 720-570/401(a)(2)
mfg_del_heroin_class_x_no_amt = (Q(final_statute__iregex=r'720-570/401\(a\)\(2\)\s*$') |
  Q(final_statute="56.5-1401-B(2)"))

# Class X Felony, >= 15g, < 100g Cocaine
# ILCS 720-570/401(a)(2)(A)
mfg_del_cocaine_15_100_g_query = Q(final_statute__iregex=r'720-570/401\(a\)\(2\)\(a\)')

# Class X Felony, >= 100g, < 400g Cocaine
# ILCS 720-570/401(a)(2)(B)
mfg_del_cocaine_100_400_g_query = Q(final_statute__iregex=r'720-570/401\(a\)\(2\)\(b\)')

# Class X Felony, >= 400g, < 900g Cocaine
# ILCS 720-570/401(a)(2)(C)
mfg_del_cocaine_400_900_g_query = Q(final_statute__iregex=r'720-570/401\(a\)\(2\)\(c\)')

# Class X Felony, >= 900g Cocaine
# ILCS 720-570/401(a)(2)(D)
mfg_del_cocaine_gt_900_g_query = Q(final_statute__iregex=r'^720-570/401\(a\)\(2\)\(d\)')

# Class 1 Felony, >= 900g Cocaine, attempted
mfg_del_att_cocaine_gt_900_g_query = Q(final_statute__in=("720-5\8-4(401-A-2-D)",
    "720-5/8-4720-570/401(A)(2)(D)"))

# Class 1 Felony, >= 200g Amphetamine
# ILCS 720-570/401(a)(6)
mfg_del_amph_gt_200_g_query = Q(final_statute__iregex=r'720-570/401\(a\)\(6\)')

# Class X Felony, >=15g, < 100g or >= 15, < 200 objects Ecstasy
# ILCS 720-570/401(a)(7.5)(A)
mfg_del_ecstasy_15_100_g_query = Q(final_statute__iregex=r'720-570[/\\]401\({0,1}a\){0,1}\(7\.5\)\({0,1}a\){0,1}')

# Class X Felony, >= 100, < 400g or >= 200, < 600 objects Ecstasy
# ILCS 720-570/401(a)(7.5)(B)
mfg_del_ecstasy_100_400_g_query = Q(final_statute__iregex=r'720-570[/\\]401\({0,1}a\){0,1}\(7\.5\)\({0,1}b\){0,1}')

# Class X Felony, >= 400g, < 900g or >= 600, < 1500 objects Ecstasy
# ILCS 720-570/401(a)(7.5)(C)
mfg_del_ecstasy_400_900_g_query = Q(final_statute__iregex=r'720-570[/\\]401\({0,1}a\){0,1}\(7\.5\)\({0,1}c\){0,1}')

# Class X, >= 900g or >= 1500 objects Ecstasy
# ILCS 720-570/401(a)(7.5)(D)
mfg_del_ecstasy_gt_900_g_query = Q(final_statute__iregex=r'720-570[/\\]401\({0,1}a\){0,1}\(7\.5\)\({0,1}d\){0,1}')

# Class X Felony, >= 30g Methaqualone
# ILCS 720-570/401(a)(9)
# ILRS 56.5-1401(a)(9)
mfg_del_methaqualone_gt_30_g_query = Q(final_statute__iregex=r'56\.5-1401-\({0,1}a\){0,1}\({0,1}9\){0,1}')

# Class X, >= 30g PCP
# ILCS 720-570/401(a)(10)
mfg_del_pcp_gt_30g_query = (Q(final_statute__iregex=r'720-570/401\(a\)\(10\)') |
    Q(final_statute="56.5-1401-A(10)"))

# Class X, >= 200g other Schedule I & II drugs
# ILCS 720-570/401(a)(11)
mfg_del_sched_1_2_gt_200_g_query = Q(final_statute__iregex=r'720-570/401\(a\)\(11\)')

# Class 1 Felony
# 720-570/401(c)

# No drug specified
mfg_del_class_1_no_drug_query = (Q(final_statute__iregex=r'720-570/401\s{0,1}\({0,1}C\){0,1}\s*$') |
    Q(final_statute="56.5-1401-C"))

# >= 1g, < 15g Heroin
# 720-570/401(c)(1)
mfg_del_heroin_1_15_g_query = Q(final_statute__iregex=r'720-570[/\\]401\({0,1}c\){0,1}\({0,1}1\){0,1}')

# >= 1g, < 15g Cocaine
# 720-570/401(c)(2)
mfg_del_cocaine_1_15_g_query = (
    Q(final_statute__iregex=r'720[-\s]570[-/]401\s{0,1}\({0,1}c\){0,1}\s{0,1}\({0,1}2\){0,1}') |
    # Records with this chargedesc have a statute of MFG/DEL 01-15 GR
    # COCAINE/ANLG,720-570/401(C)
    # From the description, it should be included
    Q(final_chrgdesc="MFG/DEL 01-15 GR COCAINE/ANLG")
)

# >= 5g, < 15g or >= 10 objects, < 15 objects LSD
# ILCS 720-570/401(c)(7)
mfg_del_lsd_5_15_g_query = Q(final_statute__iregex=r'720-570/401\(c\)\(7\)')

# >= 5g, < 15g or >= 10 objects, < 15 objects Ecstasy
# ILCS 720-570/401(c)(7.5)
mfg_del_ecstasy_5_15_g_query = Q(final_statute__iregex=r'720-570[/\\]401\({0,1}c\){0,1}\(7.5\)')

# Class 1, >= 10g, < 30g PCP
# ILCS 720-570/401(c)(11)
mfg_del_pcp_10_30_g_query = Q(final_statute__iregex=r'720-570/401\(c\)\(10\)')

# >= 50g, < 200g Other Schedule I & II drugs
# ILCS 720-570/401(c)(11)
mfg_del_sched_1_2_50_200_g_query = Q(final_statute__iregex=r'720-570/401\(c\)\(11\)')

# Manufacture or delivery of a conterfeit substance
# Class 1 Felony
# ILCS 720-570/402(a)
mfg_del_cntft_sub_query = Q(final_statute__iregex=r'56.5[-\(]1403[-A3]+\){0,1}')

# Attempted manufacture or delivery of a conterfiet substance
# Class 1 Felony, downgraded to Class 2
# ILCS 720-5/8-4 + ILCS 720-570/402(a)
mfg_del_att_cntft_sub_query = Q(final_statute__iregex=r'38-8-4[-\(]1403\s{0,1}[-A3]+\){0,1}')

# Manufacture or delivery, Class 2 Felony, other amount
# ILCS 720-570/401(d)
# Use exact values here so we don't accidentally capture the attempted or
# conspiracy charges (see below)
mfg_del_class_2_other_amt_query = Q(final_statute__in=('720-570/401(D)',
    '720-570/401(D)(I)'))

# Attempted Class 2 Felony
# Since these are attempted, they get downgraded to a Class 3 Felony
# ILCS 720-5/8-4 + ILCS 720-570/401(d)
# The statute fields for these are all over the place, making for a nasty
# regex.  Just list them.
mfg_del_att_class_2_query = Q(final_statute__in=(
    '720-5/8-4(720-5/401(D)/407(B)(2))',
    '720 5/8-4 570/401D',
    '720 5/8-4 (570/401 D)',
    '720-5/8-4 (570/401 D)',
    '720-5/8-4(720-570/401(D)(1)',
    '720-570(8-4)/401(D)(I))',
    '720-570(8-4)/401(D)(I)',
    '720-5/8-4(720-5/401(D)/407(B)(2)',
    '720-5/(8-4)401(D)',
    '720-570/401(D)(720-5/8-4))',
    '720-570/401(D)(720-5/8-4)',
))

# Conspiracy to manufacture and deliver
# ILCS 720-5/8-2 + some other charge
# Conspiracy charges get bumped down to the next lowest class of felony.
# So, for the Class 2 felony drug conviction (720-570/401(d)), the corresponding
# conspiracy charge would be a Class 3 Felony
mfg_del_conspiracy_class_2_query = Q(final_statute='720-5\8-2(570\\401D)')

# Commiting one of the other 720-570/401 crimes near a school, park or
# public housing
mfg_del_near_sch_pk_pub_hs_query = Q(final_statute__iregex=r'720-570/407\(b\)')

# Committing one of the other 720-570/401 crimes either dealing to or employing
# someone < 18
mfg_del_involving_minor_query = Q(final_statute__in=("720-570/407(a)", "720-570/407.1"))


# Class A Misdemeanor

# Attempted manufacture or delivery of Schedule IV substance
# ILCS 720-5/8-4 + ILCS 720-570/401(g)
# Normally, ILCS 720-570/401(g) would be a class 3 felony, but since it's
# attempted, we downgrade to a class A misdemeanor
mfg_del_att_sched_iv_class_3_query = Q(final_statute__icontains='720-5/8-4(720-570/401(G)')

# Attempted Manufacture or delivery of lookalike substance
# Normally, this would be a class 3 Felony, but because it's attempted, it's
# downgraded to a Class A misdemeanor
mfg_del_att_lookalike_query = (Q(final_statute__iregex=r'720-570/404\(b\)') |
    Q(final_statute__in=("720 5/8-4 570/404B", "720-570(8-4)/404(B)", "720-570 8-4/404(B)")))

# Meth
# For meth charges, the statute doesn't indicate the amount, we'll have to go
# with the charge description

# Class 2 Felony
# < 5g Meth
# ILCS 720-646/55(a)(2)(A)
mfg_del_meth_lt_5g_query = Q(final_chrgdesc__iregex=r'METH DEL(IVERY|)\s{0,1}(<|LESS THAN)\s{0,1}5 GRAMS')

# Class 1 Felony
# >= 5g, < 15g Meth
# ILCS 720-646/55(a)(2)(B)
mfg_del_meth_5_15_g_query = Q(final_chrgdesc__in=(
  "METH DELIVERY/5<15 GRAMS",
  # I'm a little less certain on this one, but couldn't figure out a better
  # place to put it.
  "POSS MANU CHEM/<15 GRAMS METH",
))

# Class 1 Felony
# Aggrevated delivery < 5g Meth
# ILCS 720-646/55(b)
mfg_del_meth_lt_5g_agg_query = Q(final_chrgdesc__in=("AGG DEL METH/PER<18/<5 GRAMS", "AGG DELMETH/SCHOOL/<5GRAMS"))

# Cannibis

# Cannibis, amount not specified
# ILCS 720-550/5
mfg_del_cannibis_no_amt_query = Q(final_statute="720-550/5")

# Class B Misdemeanor
# < 2.5g Cannibis
# ILCS 720-550/5(a)
mfg_del_cannibis_lte_2pt5_g_query = Q(final_statute__iregex=r'720-550/5\(a\)')

# Class A Misdemeanor
# > 2.5g, <= 10g Cannibis
# ILCS 720-550/5(b)
# ILRS 56.5-705(b)
mfg_del_cannibis_2pt5_10_g_query = (Q(final_statute__iregex=r'720-550[/\\]5\(b\)') |
    Q(final_statute__iexact="56.5-705-B"))

# Class 4 Felony
# > 10g, <= 30g Cannibis
# ILCS 720-550/5(c)
# ILRS 56.5-705-C
mfg_del_cannibis_10_30_g_query = (Q(final_statute__iexact="720-550/5(c)") |
    Q(final_statute__iexact="56.5-705-C"))

# Class 3 Felony
# > 30g, <= 500g Cannibis
# ILCS 720-550/5(d)
# ILRS 56.5-705-d
mfg_del_cannibis_30_500_g_query = (Q(final_statute__icontains="720-550/5(d)") |
    Q(final_statute__iexact="56.5-705-D"))

# Class 2 Felony
# > 500g, <= 2000g Cannibis
# ILCS 720-550/5(e)
# ILRS 56.5-705-e
mfg_del_cannibis_500_2000_g_query = (Q(final_statute__iregex=r'720-550/5\({0,1}e\){0,1}') |
    Q(final_statute__iexact="56.5-705-E"))

# Class 1 Felony
# > 2000g, <= 5000g Cannibis
# ILCS 720-550/5(f)
mfg_del_cannibis_2000_5000_g_query = Q(final_statute__iexact="720-550/5(f)")

# Class X Felony
# > 5000g Cannibis
# ILCS 720-550/5(g)
mfg_del_cannibis_gt_5000_g_query = Q(final_statute__iexact="720-550/5(g)")

# Delivery of Cannibis near a school

# Class 1 Felony
# > 500g, <= 2000g Cannibis near School
# ILCS 720-550/5.2(a)
mfg_del_cannibis_500_2000_g_near_sch_query = Q(final_statute__iexact="720-550/5.2(a)")

# Class 2 Felony
# > 30g, <= 500g Cannibis near School
# ILCS 720-550/5.2(b)
mfg_del_cannibis_30_500_g_near_sch_query = Q(final_statute__iexact="720-550/5.2(b)")

# Class 3 Felony
# > 10g, <= 30g Cannibis near School
# ILCS 720-550/5.2(c)
mfg_del_cannibis_10_30_g_near_sch_query = Q(final_statute__iexact="720-550/5.2(c)")

# Class 4 Felony
# > 2.5g, <= 10g Cannibis near school
# ILCS 720-550/5.2(d)
mfg_del_cannibis_2pt5_10_g_near_sch_query = Q(final_statute__iexact="720-550/5.2(d)")

# Class A Misdemeanor
# <= 2.5g Cannibis near school
# ILCS 720-550/5.2(e)
mfg_del_cannibis_lte_2pt5_g_near_sch_query = Q(final_statute__iexact="720-550/5.2(e)")

# Casual delivery of Cannibis
# Treated same as possession
# ILCS 720-550/6
# TODO: Might need to break this down by amount based on charge description
casual_del_cannibis_query = Q(final_statute="720-550/6")

# Delivery of Cannibis to a minor (it's a bit more complicated than that)
# see http://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1937&ChapterID=53
# ILCS 720-550/7
mfg_del_cannibis_to_minor_query = Q(final_statute__icontains="720-550/7")

# Delivery of drugs inside a penal institution
# I think we should exclude these from our drug counts
mfg_del_penal_inst_query = Q(final_statute__iexact="720-5/31A-1.2(c)")

# Unauthorized manufacture or delivery
# This seems to mean when someone who is otherwise registered to manufacture
# or deliver controlled substances does so in a way that is unauthorized.
# Class A Misdemeanor
mfg_del_unauth_query = Q(final_statute__iexact="720-570/406(a)(2)")

# Let's combine these into queries by felony or misdemeanor class

mfg_del_class_x_felony_query = (
    mfg_del_unkwn_class_x_query |
    mfg_del_heroin_15_100_g_query |
    mfg_del_heroin_100_400_g_query |
    mfg_del_heroin_400_900_g_query |
    mfg_del_heroin_gt_900_g_query |
    mfg_del_heroin_class_x_no_amt |
    mfg_del_cocaine_15_100_g_query |
    mfg_del_cocaine_100_400_g_query |
    mfg_del_cocaine_400_900_g_query |
    mfg_del_cocaine_gt_900_g_query |
    mfg_del_ecstasy_15_100_g_query |
    mfg_del_ecstasy_100_400_g_query |
    mfg_del_ecstasy_400_900_g_query |
    mfg_del_ecstasy_gt_900_g_query |
    mfg_del_methaqualone_gt_30_g_query |
    mfg_del_pcp_gt_30g_query |
    mfg_del_sched_1_2_gt_200_g_query |
    mfg_del_cannibis_gt_5000_g_query)

mfg_del_class_1_felony_query = (
    mfg_del_class_1_no_drug_query |
    mfg_del_heroin_1_15_g_query |
    mfg_del_att_cocaine_gt_900_g_query |
    mfg_del_cocaine_1_15_g_query |
    mfg_del_lsd_5_15_g_query |
    mfg_del_ecstasy_5_15_g_query |
    mfg_del_pcp_10_30_g_query |
    mfg_del_sched_1_2_50_200_g_query |
    mfg_del_cntft_sub_query |
    mfg_del_amph_gt_200_g_query |
    mfg_del_meth_5_15_g_query |
    mfg_del_meth_lt_5g_agg_query |
    mfg_del_cannibis_2000_5000_g_query |
    mfg_del_cannibis_500_2000_g_near_sch_query
)

mfg_del_class_2_felony_query = (
    mfg_del_att_cntft_sub_query |
    mfg_del_class_2_other_amt_query |
    mfg_del_meth_lt_5g_query |
    mfg_del_cannibis_500_2000_g_query |
    mfg_del_cannibis_30_500_g_near_sch_query
)

mfg_del_class_3_felony_query = (
    mfg_del_att_class_2_query |
    mfg_del_conspiracy_class_2_query |
    mfg_del_cannibis_30_500_g_query |
    mfg_del_cannibis_10_30_g_near_sch_query
)

mfg_del_class_4_felony_query = (
    mfg_del_cannibis_10_30_g_query |
    mfg_del_cannibis_2pt5_10_g_near_sch_query
)

mfg_del_class_a_misd_query = (
    mfg_del_att_sched_iv_class_3_query |
    mfg_del_att_lookalike_query |
    mfg_del_cannibis_2pt5_10_g_query |
    mfg_del_cannibis_lte_2pt5_g_near_sch_query |
    mfg_del_unauth_query
)

mfg_del_class_b_misd_query = mfg_del_cannibis_lte_2pt5_g_query

mfg_del_unkwn_class_query = (
    mfg_del_unkwn_query |
    mfg_del_att_unkwn_query |
    mfg_del_near_sch_pk_pub_hs_query |
    mfg_del_involving_minor_query |
    mfg_del_cannibis_no_amt_query |
    mfg_del_cannibis_to_minor_query
)

# Aggregate by drug type

# No drug could be idenitied from the statute or charge description
mfg_del_uknwn_drug_query = (
    mfg_del_unkwn_query,
    mfg_del_att_unkwn_query,
    mfg_del_unkwn_class_x_query |
    mfg_del_att_class_2_query |
    mfg_del_conspiracy_class_2_query
)

# These charges are in addition to another drug charge.  They're
# not tied to a particular drug on their own.  If you wanted to
# analyze these, you would want to look at the other charges
# in the same case.
mfg_del_no_drug_query = (
    mfg_del_near_sch_pk_pub_hs_query |
    mfg_del_involving_minor_query
)

# The charge description or statute field identified a particular
# section of the criminal code, but the code doesn't specify a
# particular drug type, or it's a drug with very little use
mfg_del_other_drug_query = (
  mfg_del_methaqualone_gt_30_g_query |
  mfg_del_att_sched_iv_class_3_query |
  mfg_del_cntft_sub_query |
  mfg_del_att_cntft_sub_query |
  mfg_del_class_2_other_amt_query |
  mfg_del_att_lookalike_query |
  mfg_del_unauth_query
)

mfg_del_heroin_query = (
    mfg_del_heroin_15_100_g_query |
    mfg_del_heroin_100_400_g_query |
    mfg_del_heroin_400_900_g_query |
    mfg_del_heroin_gt_900_g_query |
    mfg_del_heroin_class_x_no_amt |
    mfg_del_heroin_1_15_g_query
)

mfg_del_cocaine_query = (
    mfg_del_cocaine_15_100_g_query |
    mfg_del_cocaine_100_400_g_query |
    mfg_del_cocaine_400_900_g_query |
    mfg_del_cocaine_gt_900_g_query |
    mfg_del_att_cocaine_gt_900_g_query |
    mfg_del_cocaine_1_15_g_query
)

mfg_del_lsd_query = mfg_del_lsd_5_15_g_query

mfg_del_ecstasy_query = (
    mfg_del_ecstasy_15_100_g_query |
    mfg_del_ecstasy_100_400_g_query |
    mfg_del_ecstasy_400_900_g_query |
    mfg_del_ecstasy_gt_900_g_query |
    mfg_del_ecstasy_5_15_g_query
)

mfg_del_pcp_query = (
    mfg_del_pcp_gt_30g_query |
    mfg_del_pcp_10_30_g_query
)

mfg_del_sched_1_2_query = (
    mfg_del_sched_1_2_gt_200_g_query |
    mfg_del_sched_1_2_50_200_g_query
)

mfg_del_amph_query = mfg_del_amph_gt_200_g_query

mfg_del_meth_query = (
    mfg_del_meth_5_15_g_query |
    mfg_del_meth_lt_5g_agg_query |
    mfg_del_meth_lt_5g_query
)

mfg_del_cannibis_query = (
    mfg_del_cannibis_gt_5000_g_query |
    mfg_del_cannibis_2000_5000_g_query |
    mfg_del_cannibis_500_2000_g_near_sch_query |
    mfg_del_cannibis_500_2000_g_query |
    mfg_del_cannibis_30_500_g_near_sch_query |
    mfg_del_cannibis_30_500_g_query |
    mfg_del_cannibis_10_30_g_near_sch_query |
    mfg_del_cannibis_10_30_g_query |
    mfg_del_cannibis_2pt5_10_g_near_sch_query |
    mfg_del_cannibis_2pt5_10_g_query |
    mfg_del_cannibis_lte_2pt5_g_near_sch_query |
    mfg_del_cannibis_lte_2pt5_g_query |
    mfg_del_cannibis_no_amt_query |
    mfg_del_cannibis_to_minor_query
)

# All manufacturing or delivering drug charges
mfg_del_query = (
    mfg_del_unkwn_class_x_query |
    mfg_del_heroin_15_100_g_query |
    mfg_del_heroin_100_400_g_query |
    mfg_del_heroin_400_900_g_query |
    mfg_del_heroin_gt_900_g_query |
    mfg_del_heroin_class_x_no_amt |
    mfg_del_cocaine_15_100_g_query |
    mfg_del_cocaine_100_400_g_query |
    mfg_del_cocaine_400_900_g_query |
    mfg_del_cocaine_gt_900_g_query |
    mfg_del_ecstasy_15_100_g_query |
    mfg_del_ecstasy_100_400_g_query |
    mfg_del_ecstasy_400_900_g_query |
    mfg_del_ecstasy_gt_900_g_query |
    mfg_del_methaqualone_gt_30_g_query |
    mfg_del_pcp_gt_30g_query |
    mfg_del_sched_1_2_gt_200_g_query |
    mfg_del_cannibis_gt_5000_g_query |
    mfg_del_class_1_no_drug_query |
    mfg_del_heroin_1_15_g_query |
    mfg_del_att_cocaine_gt_900_g_query |
    mfg_del_cocaine_1_15_g_query |
    mfg_del_lsd_5_15_g_query |
    mfg_del_ecstasy_5_15_g_query |
    mfg_del_pcp_10_30_g_query |
    mfg_del_sched_1_2_gt_200_g_query |
    mfg_del_cntft_sub_query |
    mfg_del_amph_gt_200_g_query |
    mfg_del_meth_5_15_g_query |
    mfg_del_meth_lt_5g_agg_query |
    mfg_del_cannibis_2000_5000_g_query |
    mfg_del_cannibis_500_2000_g_near_sch_query |
    mfg_del_att_cntft_sub_query |
    mfg_del_class_2_other_amt_query |
    mfg_del_meth_lt_5g_query |
    mfg_del_cannibis_500_2000_g_query |
    mfg_del_cannibis_30_500_g_near_sch_query |
    mfg_del_att_class_2_query |
    mfg_del_conspiracy_class_2_query |
    mfg_del_cannibis_30_500_g_query |
    mfg_del_cannibis_10_30_g_near_sch_query |
    mfg_del_cannibis_10_30_g_query |
    mfg_del_cannibis_2pt5_10_g_near_sch_query |
    mfg_del_att_sched_iv_class_3_query |
    mfg_del_att_lookalike_query |
    mfg_del_cannibis_2pt5_10_g_query |
    mfg_del_cannibis_lte_2pt5_g_near_sch_query |
    mfg_del_unauth_query |
    mfg_del_cannibis_lte_2pt5_g_query |
    mfg_del_unkwn_query |
    mfg_del_att_unkwn_query |
    mfg_del_near_sch_pk_pub_hs_query |
    mfg_del_involving_minor_query |
    mfg_del_cannibis_no_amt_query |
    mfg_del_cannibis_to_minor_query
)

# TODO: Include these somewhware. It's treated as possession
# casual_del_cannibis_query

def filter_method_from_query(q):
    """
    Return a method that just runs QuerySet.filter() with the given parameter
    """
    def filter_fn(self):
        return self.filter(q)

    return filter_fn

class DrugQuerySetMixinMeta(type):
    def __init__(cls, name, bases, dct):
        super(DrugQuerySetMixinMeta, cls).__init__(name, bases, dct)

        # Iterate through all the queries in this module and
        # create methods that filter based on all the queries
        # we've defined above.  For example,
        # cls.mfg_del() is equivalent to cls.filter(mfg_del_query)
        for k, v in globals().items():
            if k.startswith('mfg_del_') and k.endswith('_query'):
                attr = k.replace('_query', '')
                setattr(cls, attr, filter_method_from_query(v))


class DrugQuerySetMixin(object, metaclass=DrugQuerySetMixinMeta):
    """
    QuerySet mixin that provides methods to based on charge descriptions and dispositions that represent drug crimes
    """
    # Python 3 ignores this.  Keep it here for possible backward
    # compatibility
    __metaclass__ = DrugQuerySetMixinMeta
