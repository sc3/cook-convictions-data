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
    # Casual delivery of cannabis, treat as possession based on statute
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
mfg_del_sched_1_2_gte_200_g_query = Q(final_statute__iregex=r'720-570/401\(a\)\(11\)')

# Class 1 Felony
# 720-570/401(c)

# No drug specified
mfg_del_class_1_no_drug_query = (Q(final_statute__iregex=r'720-570/401\s{0,1}\({0,1}C\){0,1}\s*$') |
    Q(final_statute="56.5-1401-C"))

# >= 1g, < 15g Heroin
# 720-570/401(c)(1)
mfg_del_heroin_1_15_g_query = Q(final_statute__iregex=r'720[- ]570[/\\]401\({0,1}c\){0,1}\({0,1}1\){0,1}')

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
    '720-570/401(D)(I)', '720-570/401-D'))

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
    '720 5/8-4 570 401(D)',
))

# Conspiracy to manufacture and deliver
# ILCS 720-5/8-2 + some other charge
# Conspiracy charges get bumped down to the next lowest class of felony.
# So, for the Class 2 felony drug conviction (720-570/401(d)), the corresponding
# conspiracy charge would be a Class 3 Felony
mfg_del_conspiracy_class_2_query = Q(final_statute='720-5\8-2(570\\401D)')

# Commiting one of the other 720-570/401 crimes near a school, park or
# public housing
# ILCS-570/407(b)
mfg_del_near_sch_pk_pub_hs_query = (
    Q(final_statute__iregex=r'720-570/407\(b\)') |
    Q(final_statute__iexact='56.5.1407-B(2)')
)

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

# Chemical breakdown of illicit controlled substance 
# It is unlawful for any person to possess any substance with the intent to use
# the substance to facilitate the manufacture of any controlled substance other
# than methamphetamine, any counterfeit substance, or any controlled substance
# analog other than as authorized by this Act.
# Class 4 felony
# ILCS 720-570/401.5
mfg_del_chemical_breakdown_query = Q(final_statute='720-570/401.5(a-5)') 

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

# cannabis

# cannabis, amount not specified
# ILCS 720-550/5
mfg_del_cannabis_no_amt_query = Q(final_statute="720-550/5")

# Class B Misdemeanor
# < 2.5g cannabis
# ILCS 720-550/5(a)
mfg_del_cannabis_lte_2pt5_g_query = Q(final_statute__iregex=r'720-550/5\(a\)')

# Class A Misdemeanor
# > 2.5g, <= 10g cannabis
# ILCS 720-550/5(b)
# ILRS 56.5-705(b)
mfg_del_cannabis_2pt5_10_g_query = (
    Q(final_statute__iregex=r'720-550[/\\]5[-(/]+b\){0,1}') |
    Q(final_statute__iexact="56.5-705-B"))

# Class 4 Felony
# > 10g, <= 30g cannabis
# ILCS 720-550/5(c)
# ILRS 56.5-705-C
mfg_del_cannabis_10_30_g_query = (
    Q(final_statute__iregex=r'720-550/5[-(]c\){0,1}') |
    Q(final_statute__iexact="56.5-705-C"))

# Class 3 Felony
# > 30g, <= 500g cannabis
# ILCS 720-550/5(d)
# ILRS 56.5-705-d
mfg_del_cannabis_30_500_g_query = (Q(final_statute__icontains="720-550/5(d)") |
    Q(final_statute__iexact="56.5-705-D"))

# Class 2 Felony
# > 500g, <= 2000g cannabis
# ILCS 720-550/5(e)
# ILRS 56.5-705-e
mfg_del_cannabis_500_2000_g_query = (
    Q(final_statute__iregex=r'720-550/5\({0,1}e\){0,1}') |
    Q(final_statute__iexact="56.5-705-E"))

# Class 1 Felony
# > 2000g, <= 5000g cannabis
# ILCS 720-550/5(f)
mfg_del_cannabis_2000_5000_g_query = Q(final_statute__iexact="720-550/5(f)")

# Class X Felony
# > 5000g cannabis
# ILCS 720-550/5(g)
mfg_del_cannabis_gt_5000_g_query = Q(final_statute__iexact="720-550/5(g)")

# Delivery of cannabis near a school

# Class 1 Felony
# > 500g, <= 2000g cannabis near School
# ILCS 720-550/5.2(a)
mfg_del_cannabis_500_2000_g_near_sch_query = Q(final_statute__iexact="720-550/5.2(a)")

# Class 2 Felony
# > 30g, <= 500g cannabis near School
# ILCS 720-550/5.2(b)
mfg_del_cannabis_30_500_g_near_sch_query = Q(final_statute__iexact="720-550/5.2(b)")

# Class 3 Felony
# > 10g, <= 30g cannabis near School
# ILCS 720-550/5.2(c)
mfg_del_cannabis_10_30_g_near_sch_query = Q(final_statute__iexact="720-550/5.2(c)")

# Class 4 Felony
# > 2.5g, <= 10g cannabis near school
# ILCS 720-550/5.2(d)
mfg_del_cannabis_2pt5_10_g_near_sch_query = Q(final_statute__iexact="720-550/5.2(d)")

# Class A Misdemeanor
# <= 2.5g cannabis near school
# ILCS 720-550/5.2(e)
mfg_del_cannabis_lte_2pt5_g_near_sch_query = Q(final_statute__iexact="720-550/5.2(e)")

# Delivery of cannabis to a minor (it's a bit more complicated than that)
# see http://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1937&ChapterID=53
# ILCS 720-550/7
mfg_del_cannabis_to_minor_query = Q(final_statute__icontains="720-550/7")

# Delivery of drugs inside a penal institution
# I think we should exclude these from our drug counts
mfg_del_penal_inst_query = Q(final_statute__iexact="720-5/31A-1.2(c)")

# Unauthorized manufacture or delivery
# This seems to mean when someone who is otherwise registered to manufacture
# or deliver controlled substances does so in a way that is unauthorized.
# Class A Misdemeanor
mfg_del_unauth_query = Q(final_statute__iexact="720-570/406(a)(2)")

# Manufacture or Delivery by Felony or Misdemeanor Class

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
    mfg_del_sched_1_2_gte_200_g_query |
    mfg_del_cannabis_gt_5000_g_query)

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
    mfg_del_cannabis_2000_5000_g_query |
    mfg_del_cannabis_500_2000_g_near_sch_query
)

mfg_del_class_2_felony_query = (
    mfg_del_att_cntft_sub_query |
    mfg_del_class_2_other_amt_query |
    mfg_del_meth_lt_5g_query |
    mfg_del_cannabis_500_2000_g_query |
    mfg_del_cannabis_30_500_g_near_sch_query
)

mfg_del_class_3_felony_query = (
    mfg_del_att_class_2_query |
    mfg_del_conspiracy_class_2_query |
    mfg_del_cannabis_30_500_g_query |
    mfg_del_cannabis_10_30_g_near_sch_query
)

mfg_del_class_4_felony_query = (
    mfg_del_cannabis_10_30_g_query |
    mfg_del_cannabis_2pt5_10_g_near_sch_query |
    mfg_del_chemical_breakdown_query
)

mfg_del_class_a_misd_query = (
    mfg_del_att_sched_iv_class_3_query |
    mfg_del_att_lookalike_query |
    mfg_del_cannabis_2pt5_10_g_query |
    mfg_del_cannabis_lte_2pt5_g_near_sch_query |
    mfg_del_unauth_query
)

mfg_del_class_b_misd_query = mfg_del_cannabis_lte_2pt5_g_query

mfg_del_unkwn_class_query = (
    mfg_del_unkwn_query |
    mfg_del_att_unkwn_query |
    mfg_del_near_sch_pk_pub_hs_query |
    mfg_del_involving_minor_query |
    mfg_del_cannabis_no_amt_query |
    mfg_del_cannabis_to_minor_query
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
  mfg_del_unauth_query |
  mfg_del_chemical_breakdown_query
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
    mfg_del_sched_1_2_gte_200_g_query |
    mfg_del_sched_1_2_50_200_g_query
)

mfg_del_amph_query = mfg_del_amph_gt_200_g_query

mfg_del_meth_query = (
    mfg_del_meth_5_15_g_query |
    mfg_del_meth_lt_5g_agg_query |
    mfg_del_meth_lt_5g_query
)

mfg_del_cannabis_query = (
    mfg_del_cannabis_gt_5000_g_query |
    mfg_del_cannabis_2000_5000_g_query |
    mfg_del_cannabis_500_2000_g_near_sch_query |
    mfg_del_cannabis_500_2000_g_query |
    mfg_del_cannabis_30_500_g_near_sch_query |
    mfg_del_cannabis_30_500_g_query |
    mfg_del_cannabis_10_30_g_near_sch_query |
    mfg_del_cannabis_10_30_g_query |
    mfg_del_cannabis_2pt5_10_g_near_sch_query |
    mfg_del_cannabis_2pt5_10_g_query |
    mfg_del_cannabis_lte_2pt5_g_near_sch_query |
    mfg_del_cannabis_lte_2pt5_g_query |
    mfg_del_cannabis_no_amt_query |
    mfg_del_cannabis_to_minor_query
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
    mfg_del_sched_1_2_gte_200_g_query |
    mfg_del_cannabis_gt_5000_g_query |
    mfg_del_class_1_no_drug_query |
    mfg_del_heroin_1_15_g_query |
    mfg_del_att_cocaine_gt_900_g_query |
    mfg_del_cocaine_1_15_g_query |
    mfg_del_lsd_5_15_g_query |
    mfg_del_ecstasy_5_15_g_query |
    mfg_del_pcp_10_30_g_query |
    mfg_del_cntft_sub_query |
    mfg_del_amph_gt_200_g_query |
    mfg_del_meth_5_15_g_query |
    mfg_del_meth_lt_5g_agg_query |
    mfg_del_cannabis_2000_5000_g_query |
    mfg_del_cannabis_500_2000_g_near_sch_query |
    mfg_del_att_cntft_sub_query |
    mfg_del_class_2_other_amt_query |
    mfg_del_meth_lt_5g_query |
    mfg_del_cannabis_500_2000_g_query |
    mfg_del_cannabis_30_500_g_near_sch_query |
    mfg_del_att_class_2_query |
    mfg_del_conspiracy_class_2_query |
    mfg_del_cannabis_30_500_g_query |
    mfg_del_cannabis_10_30_g_near_sch_query |
    mfg_del_cannabis_10_30_g_query |
    mfg_del_cannabis_2pt5_10_g_near_sch_query |
    mfg_del_att_sched_iv_class_3_query |
    mfg_del_att_lookalike_query |
    mfg_del_cannabis_2pt5_10_g_query |
    mfg_del_cannabis_lte_2pt5_g_near_sch_query |
    mfg_del_unauth_query |
    mfg_del_cannabis_lte_2pt5_g_query |
    mfg_del_unkwn_query |
    mfg_del_att_unkwn_query |
    mfg_del_near_sch_pk_pub_hs_query |
    mfg_del_involving_minor_query |
    mfg_del_cannabis_no_amt_query |
    mfg_del_cannabis_to_minor_query |
    mfg_del_chemical_breakdown_query
)

# A catchall for drug possesion charges that are clearly in 
# ILCS 720-570/402, but where the class of charge, type of
# drug and amount aren't specified
poss_ctl_sub_no_drug_no_amt_query = Q(final_statute__in=(
    # There's no ILCS 720-570/402(f).  Just throw it in here
    '720-570/402(F)',
    'PCS',
    '56.5-1402-B',
))

# Same as above, but attempted possession
poss_ctl_sub_att_no_drug_no_amt_query = (
    Q(final_statute__in=(
        '720-570/8-4(720-570/402)',
        '720-5/8-4-A//720-570/402',
        '38-8-4/56.5-1402',
        '720-570/8-4',
        '720-570/8-4(A)',
    )) |
    Q(final_chrgdesc='ATTEMPT POSS CON SUB', final_statute='720-5/8-4(A)')
)

# Possession of controlled substance
# Class 1 Felony
# ILCS 720-570/402(a)
poss_ctl_sub_class_1_unkwn_drug_query = Q(final_statute__in=(
    '720-570/402A',
    '56.5-1402-A',
))

# Possession >= 15g Heroin
# Class 1 Felony
# ILCS 720-570/402(a)(1)
# Further subsections specify more exact amount ranges.  This query is to
# catch the records that don't further specify the amount.
poss_heroin_gte_15_g_query = Q(final_statute__iexact='720-570/402(a)(1)')

# Possession >= 15g, < 100g Heroin
# Class 1 Felony
# ILCS 720-570/402(a)(1)(a)
poss_heroin_15_100_g_query = Q(final_statute__iexact='720-570/402(a)(1)(a)')

# Possession >= 100g, < 400 g Heroin
# Class 1 Felony
# ILCS 720-570/402(a)(1)(b)
poss_heroin_100_400_g_query = Q(final_statute__iexact='720-570/402(a)(1)(b)')

# Possession >= 400g, < 900 g Heroin
# Class 1 Felony
# ILCS 720-570/402(a)(1)(c)
poss_heroin_400_900_g_query = Q(final_statute__iexact='720-570/402(a)(1)(c)')

# Possession >= 900 g Heroin
# Class 1 Felony
# ILCS 720-570/402(a)(1)(d)
poss_heroin_gte_900_g_query = Q(final_statute__iexact='720-570/402(a)(1)(d)')

# Possession >= 15g Cocaine
# Class 1 Felony
# ILCS 720-570/402(a)(2)
poss_cocaine_gte_15_g_query = Q(final_statute__iexact='720-570/402(a)(2)')

# Possession >= 15g, < 100g Cocaine
# Class 1 Felony
# ILCS 720-570/402(a)(2)(a)
poss_cocaine_15_100_g_query = (Q(final_statute='720-570/402-A-2-A') |
    Q(final_statute__iexact='720-570/402(a)(2)(a)')
)

# Attempted Possession >= 15g, < 100g Cocaine
# Class 2 Felony
# ILCS 720-5/8-4 + ILCS 720-570/402(a)(2)(a)
poss_cocaine_att_15_100_g_query = Q(final_statute__in=(
    '720-5/(8-4)402(2)(A)',
    '720-5/8-4 570/402A2A',
)) 

# Possession >= 100g, < 400g Cocaine
# Class 1 Felony
# ILCS 720-570/402(a)(2)(b)
poss_cocaine_100_400_g_query = Q(final_statute__iexact='720-570/402(a)(2)(b)')

# Possession >= 400g, < 900g Cocaine
# Class 1 Felony
# ILCS 720-570/402(a)(2)(c)
poss_cocaine_400_900_g_query = Q(final_statute__iexact='720-570/402(a)(2)(c)')

# Possession >= 900g Cocaine
# Class 1 Felony
# ILCS 720-570/402(a)(2)(d)
poss_cocaine_gte_900_g_query = Q(final_statute__iexact='720-570/402(a)(2)(d)')

# Possession >= 15g, < 100g Morphine
# Class 1 Felony
# ILCS 720-570/402(a)(3)(a)
poss_morphine_15_100_g_query = Q(final_statute__iexact='720-570/402(a)(3)(a)')

# Possession >= 200g Barbituric Acid
# Class 1 Felony
# ILCS 720-570/402(a)(5)
poss_barbituric_gte_200_g_query = Q(final_statute__iexact='720-570/402(a)(5)')

# Possession >= 200g Amphetamine
# Class 1 Felony
# ILCS 720-570/402(a)(6)
poss_amphetamine_gte_200_g_query = Q(final_statute__iexact='720-570/402(a)(6)')

# Possession Look-Alike Substance
# Class C Misdemeanor
# ILCS 720-570/404(c)
poss_lookalike_query = Q(final_statute__iexact='720-570/404(c)')

# Illegal Possession of Script Forms
# Class 4 Felony
# ILCS 720-570/406.2
# It looks like many of these have a statue of ILCS 720-570/406(b)(6), which
# is blank in web versions of the criminal code.
# Perhaps this section was moved to ILCS 720-570/406.2
poss_script_form_query = (
    Q(final_statute__iexact='720-570/406(b)(6)') |
    Q(final_statute__istartswith='720-570/406.2')
)

# Attempted Illegal Possession of Script Forms
# Class 4 Felony, downgraded to Class A Misdemeanor
# ILCS 720-5/8-4 + ILCS 720-570/406.2
# It looks like many of these have a statue of ILCS 720-570/406(b)(6), which
# is blank in web versions of the criminal code.
poss_att_script_form_query = Q(final_statute__iregex=r'720-5/8-4(-A|)[^\w]*720-570/406[-/(]*B[-()]*6')

# Possession >= 15g, < 100g or >= 15 objects, < 200 objects LSD
# Class 1 Felony
# ILCS 720-570/402(a)(7)(A)
poss_lsd_15_100_g_query = Q(final_statute__icontains='720-570/402(a)(7)(A)')

# Possession >= 400g, < 900g or >= 600 objects, < 1500 objects LSD
# Class 1 Felony
# ILCS 720-570/402(a)(7)(C)
poss_lsd_400_900_g_query = Q(final_statute__icontains='720-570/402(a)(7)(C)')

# Possession >= 15g, < 100g or >= 15 objects, < 200 objects Ecstasy
# Class 1 Felony
# ILCS 720-570/402(a)(7.5)(A)
poss_ecstasy_15_100_g_query = Q(final_statute__icontains='720-570/402(A)(7.5)(A)')

# Possession >= 100g, < 400g or >= 200 objects, < 600 objects
# Class 1 Felony
# ILCS 720-570/402(a)(7.5)(B)
poss_ecstasy_100_400_g_query = Q(final_statute__icontains='720-570/402(a)(7.5)(B)')

# Possession >= 30g PCP
# Class 1 Felony
# ILCS 720-570/402(a)(10)
poss_pcp_gte_30_g_query = Q(final_statute__iexact='720-570/402(a)(10)')

# Possession >= 30g Ketamine
# Class 1 Felony
# ILCS 720-570/402(a)(10.5)
poss_ketamine_gte_30_g_query = Q(final_statute__iexact='720-570/402(a)(10.5)')

# Possession >= 200g other Schedule ! & !!
# Class 1 Felony
# ILCS 720-570/402(a)(11)
poss_sched_1_2_gte_200_g_query = Q(final_statute__iexact='720-570/402(a)(11)')

# Possession, no class
# This represents an additional penalty on top of a ILCS 720-570/402(a)
# ILCS 720-570/402(b) / ILRS 56.5-1402(b)
poss_no_class_no_drug_query = Q(final_statute__in=('56.5-1402-B'))

# Possession, amount less than the ones specifed in ILCS 720-570/402(a)
# Class 4 Felony
# ILCS 720-570/402(c)
poss_ctl_sub_class_4_query = Q(final_statute__iregex=r'^720[- ]570/402\s{0,1}\({0,1}-{0,1}c\){0,1}$')

# Attempted Possession, amount less than the ones specified in ILCS
# 720-570/402(a)
# Class 4 Felony, downgraded to Class A misdemeanor
# ILCS 720-5/8-4 + ILCS 720-570/402(c)
poss_ctl_sub_att_class_4_query = (
    Q(final_statute__iregex=r'720[-\s/]{0,1}(5|)(70|)[-/\s(]*8-4[-)(]*A{0,1}[(\s/)]*(720|)[-/]*(5|)(70|)[-/]402[-\s(]*c{0,1}') |
    Q(final_statute__iregex=r'720-570[-/]*(5|)[/(]*8-4[()A(/]*402[\s(]*c') |
    Q(final_statute__iregex=r'720-570/402\(c\)(5|)/8-4')
)

# Possession Steroids
# Class C Misdemeanor (Class B for recent repeat offenders, but we'll gloss
# over that here)
# ILCS 720-570/402(d)
poss_steroids_query = (
    Q(final_statute__istartswith='720-570/402(d)') |
    # There is no ILCS 720-5/402(d), assuming this is a typo and
    # 720-570/402(d) was intended
    Q(final_statute__iexact='720-5/402(d)')
)

# Meth

# Meth charges are weird because they have statutes that are both in
# ILCS 720-570/402(a)(6.5) (which seems deprecated) and 
# ILCS 720-646/60.  For the records with ILCS 720-646/60 statutes, the
# statute isn't specific enough to identify the amount, so we rely on
# the charge description.

# Possession < 5g Meth
# Class 3 Felony
# ILCS 720-646/60(b)(1)
poss_meth_lt_5g_query = (
    Q(final_statute__iexact='720-646/60(b)(1)') |
    Q(final_chrgdesc__iregex=r'POSSESSION OF METH<\s*5\s*GRA(MS|)') |
    Q(final_chrgdesc='POSS.OF METH')
)

# Attempted possession < 5g meth
# ILCS 720-5/8-4 + ILCS 720-646/60(a)
# Class 3 Felony, downgraded to Class A Misdemeanor
# The statute or the charge description of these records don't indicate amount,
# but the chrgclass fields indicate that the the original class was a class 3
# felony and that the final class was a class A misdemeanor.  It's safe to
# assume from this that we're talking about possession < 5g
poss_meth_att_lt_5g_query = Q(final_statute__iregex=r'720-5/8-4[\s(]+720-646/60[(]*A[)]+')

# Possession >= 5g, < 15g Meth
# Class 2 Felony
# ILCS 720-646/60(b)(2)
poss_meth_5_15_g_query = (
    Q(final_chrgdesc__istartswith='POSSESSION OF METH/5<15 G') |
    Q(final_statute__iregex=r'720-646/60A{0,1}-B[-(]2[)]*')
)

# Possession >= 15g, < 100g Meth
# Class 1 Felony
# ILCS 720-646/60(b)(3)
# Some of these records have weird ILCS references like ILCS
# 720-570/402(a)(6.5)(a)
poss_meth_15_100_g_query = (
    Q(final_statute__iexact='720-570/402(a)(6.5)(a)') |
    Q(final_statute__iexact='720-570/402(6.5)a') |
    Q(final_chrgdesc__iexact='POSSESSION OF METH/15<100GRAMS')
)

# Possession >= 400 g, < 900g Meth
# Class X Felony
# ILCS 720-646/60(b)(5)
# Some of these records have weird ILCS references like ILCS
# 720-570/402(a)(6.5)(c)
poss_meth_400_900_g_query = Q(final_statute='720-570/402-A-6.5-C') 

# Possession >= 900g Meth
# Class X Felony
# ILCS 720-646/60(b)(6)
# Some of these records have weird ILCS references like ILCS
# 720-570/402(a)(6.5)(d)
poss_meth_gte_900_g_query = Q(final_statute='720-570-402(A)(6.5)D')

# Possession amount not specified Cannabis
# ILCS 720-550/4
# The ILRS reference below "56-1/2-440(D)" is wonky becase I couldn't
# find a corresponding ILCS reference.
poss_cannabis_amt_unknwn_query = Q(final_statute__in=('720-550/4.',
    '56-1/2-440(D)'))

# Attempted Possession amount not specified Cannabis
# ILCS 720-5/8-4 + ILCS 720-550/4
poss_cannabis_att_amt_unknwn_query = Q(final_statute='720/550-8-4')

# Possession <= 2.5g Cannabis
# Class C Misdemeanor
# ILCS 720-550/4(a)
poss_cannabis_lte_2pt5_g_query = Q(final_statute__iexact='720-550/4(a)')

# Possession > 2.5g, <= 10g Cannabis
# Class B Misdemeanor
# ILCS 720-550/4(b)
poss_cannabis_2pt5_10_g_query = Q(final_statute__iexact='720-550/4(b)')

# Possession > 10g, <= 30g Cannabis
# Class 4 Felony
# ILCS 720-550/4(c)
poss_cannabis_10_30_g_query = Q(final_statute__iregex='720-550(.0|)/4[-(]{0,1}c[)]{0,1}')

# Possession > 30g, <= 500g Cannabis
# Class 4 Felony (class 3 for subsequent offenses)
# ILCS 720-550/4(d)
poss_cannabis_30_500_g_query = (
    Q(final_statute__iregex=r'720[-\s](550|570)/4\(d\)') |
    Q(final_chrgdesc='POSS CANNABIS 30-500 GRAMS')
)

# Possession > 500g, <= 2000g Cannabis
# Class 3 Felony
# ILCS 720-550/4(e)
poss_cannabis_500_2000_g_query = Q(final_statute__iexact='720-550/4(e)')

# Possession > 2000g, 5000g Cannabis
# Class 2 Felony
# ILCS 720-550/4(f)
poss_cannabis_2000_5000_g_query = Q(final_statute__iregex='720-550/4[-(]+f\)')

# Possession > 5000g Cannabis
# Class 1 Felony
# ILCS 720-550/4(g)
poss_cannabis_gt_5000_g_query = Q(final_statute__iexact='720-550/4(g)')

# Casual delivery of cannabis
# Treated same as possession
# ILCS 720-550/6

# Casual delivery > 2.5g, <= 10g cannabis
# Class B Misdemeanor 
# ILCS 720-550/6
casual_del_cannabis_2pt5_10_g_query = Q(final_statute='720-550/6',
    final_chrgdesc='CASUAL DEL CAN/2.5 - 10 GRAMS')

# Casual delivery > 10g, <= 30g cannabis
# Class 4 Felony
# ILCS 720-550/6
casual_del_cannabis_10_30_g_query = Q(final_statute='720-550/6',
    final_chrgdesc__iregex=r'CASUAL DEL CAN/10-30 GRAMS{0,1}')

# Casual delivery > 30g, <= 500g Cannabis
# Class 4 Felony (class 3 for susequent offenses)
# ILCS 720-550/6
casual_del_cannabis_30_500_g_query = Q(final_statute='720-550/6',
    final_chrgdesc__iexact=r'CAS DEL CAN/30-500 GRAMS/SUBQ')

# Possession of Cannabis plants
# ILCS 720-550/8

# Possession > 5, <= 20 Cannabis plants
# Class 4 Felony
# ILCS 720-550/8(b) 
poss_cannabis_plants_5_20_query = Q(final_statute__iexact='720-550/8(B)')

# Possession by Felony or Misdemeanor Class

poss_unkwn_class_query = (
    poss_ctl_sub_no_drug_no_amt_query |
    poss_ctl_sub_att_no_drug_no_amt_query |
    poss_cannabis_amt_unknwn_query |
    poss_cannabis_att_amt_unknwn_query
)

poss_no_class_query = poss_no_class_no_drug_query

poss_class_x_felony_query = (
    poss_meth_400_900_g_query |
    poss_meth_gte_900_g_query
)

poss_class_1_felony_query = (
    poss_ctl_sub_class_1_unkwn_drug_query |
    poss_heroin_gte_15_g_query |
    poss_heroin_15_100_g_query |
    poss_heroin_100_400_g_query |
    poss_heroin_400_900_g_query |
    poss_heroin_gte_900_g_query |
    poss_cocaine_gte_15_g_query |
    poss_cocaine_15_100_g_query |
    poss_cocaine_100_400_g_query |
    poss_cocaine_400_900_g_query |
    poss_cocaine_gte_900_g_query |
    poss_morphine_15_100_g_query |
    poss_barbituric_gte_200_g_query |
    poss_amphetamine_gte_200_g_query |
    poss_lsd_15_100_g_query |
    poss_lsd_400_900_g_query |
    poss_ecstasy_15_100_g_query |
    poss_ecstasy_100_400_g_query |
    poss_pcp_gte_30_g_query |
    poss_ketamine_gte_30_g_query |
    poss_sched_1_2_gte_200_g_query |
    poss_meth_15_100_g_query |
    poss_cannabis_gt_5000_g_query
)

poss_class_2_felony_query = (
    poss_cocaine_att_15_100_g_query |
    poss_meth_5_15_g_query |
    poss_cannabis_2000_5000_g_query
)

poss_class_3_felony_query = (
    poss_meth_lt_5g_query |
    poss_cannabis_500_2000_g_query
)

poss_class_4_felony_query = (
    poss_script_form_query |
    poss_ctl_sub_class_4_query |
    poss_cannabis_10_30_g_query |
    poss_cannabis_30_500_g_query |
    casual_del_cannabis_10_30_g_query |
    casual_del_cannabis_30_500_g_query |
    poss_cannabis_plants_5_20_query
)

poss_class_a_misd_query = (
    poss_att_script_form_query |
    poss_ctl_sub_att_class_4_query |
    poss_meth_att_lt_5g_query
)


poss_class_b_misd_query = (
    poss_cannabis_2pt5_10_g_query |
    casual_del_cannabis_2pt5_10_g_query
)

poss_class_c_misd_query = (
    poss_lookalike_query |
    poss_steroids_query |
    poss_cannabis_lte_2pt5_g_query
)

# Drug possession by drug type

poss_unkwn_drug_query = (
    poss_ctl_sub_no_drug_no_amt_query |
    poss_ctl_sub_att_no_drug_no_amt_query |
    poss_ctl_sub_class_1_unkwn_drug_query |
    poss_ctl_sub_class_4_query |
    poss_ctl_sub_att_class_4_query
)

poss_heroin_query = (
    poss_heroin_gte_15_g_query |
    poss_heroin_15_100_g_query |
    poss_heroin_100_400_g_query |
    poss_heroin_400_900_g_query |
    poss_heroin_gte_900_g_query
)

poss_cocaine_query = (
    poss_cocaine_gte_15_g_query |
    poss_cocaine_15_100_g_query |
    poss_cocaine_att_15_100_g_query |
    poss_cocaine_100_400_g_query |
    poss_cocaine_400_900_g_query |
    poss_cocaine_gte_900_g_query
)

poss_morphine_query = poss_morphine_15_100_g_query

poss_barbituric_query = poss_barbituric_gte_200_g_query

poss_amphetamine_query = poss_amphetamine_gte_200_g_query

poss_lsd_query = (
    poss_lsd_15_100_g_query |
    poss_lsd_400_900_g_query
)

poss_ecstasy_query = (
    poss_ecstasy_15_100_g_query |
    poss_ecstasy_100_400_g_query
)

poss_pcp_query = poss_pcp_gte_30_g_query

poss_ketamine_query = poss_ketamine_gte_30_g_query

# Remember poss_steroids_query is defiend above

poss_meth_query = (
    poss_meth_lt_5g_query |
    poss_meth_5_15_g_query |
    poss_meth_15_100_g_query |
    poss_meth_400_900_g_query |
    poss_meth_gte_900_g_query
)

poss_cannabis_query = (
    poss_cannabis_amt_unknwn_query |
    poss_cannabis_att_amt_unknwn_query |
    poss_cannabis_lte_2pt5_g_query |
    poss_cannabis_2pt5_10_g_query |
    poss_cannabis_10_30_g_query |
    poss_cannabis_30_500_g_query |
    poss_cannabis_500_2000_g_query |
    poss_cannabis_gt_5000_g_query |
    casual_del_cannabis_2pt5_10_g_query |
    casual_del_cannabis_10_30_g_query |
    casual_del_cannabis_30_500_g_query |
    poss_cannabis_plants_5_20_query
)

poss_sched_1_2_query = poss_sched_1_2_gte_200_g_query

poss_other_drug_query = (
    poss_lookalike_query |
    poss_att_script_form_query |
    poss_script_form_query
)

poss_no_drug_query = poss_no_class_no_drug_query

# All drug possession charges

poss_query = (
    poss_ctl_sub_no_drug_no_amt_query |
    poss_ctl_sub_att_no_drug_no_amt_query |
    poss_ctl_sub_class_1_unkwn_drug_query |
    poss_heroin_gte_15_g_query |
    poss_heroin_15_100_g_query |
    poss_heroin_100_400_g_query |
    poss_heroin_400_900_g_query |
    poss_heroin_gte_900_g_query |
    poss_cocaine_gte_15_g_query |
    poss_cocaine_15_100_g_query |
    poss_cocaine_att_15_100_g_query |
    poss_cocaine_100_400_g_query |
    poss_cocaine_400_900_g_query |
    poss_cocaine_gte_900_g_query |
    poss_morphine_15_100_g_query |
    poss_barbituric_gte_200_g_query |
    poss_amphetamine_gte_200_g_query |
    poss_lookalike_query |
    poss_script_form_query |
    poss_att_script_form_query |
    poss_lsd_15_100_g_query |
    poss_lsd_400_900_g_query |
    poss_ecstasy_15_100_g_query |
    poss_ecstasy_100_400_g_query |
    poss_pcp_gte_30_g_query |
    poss_ketamine_gte_30_g_query |
    poss_sched_1_2_gte_200_g_query |
    poss_ctl_sub_class_4_query |
    poss_ctl_sub_att_class_4_query |
    poss_steroids_query |
    poss_meth_lt_5g_query |
    poss_meth_att_lt_5g_query |
    poss_meth_5_15_g_query |
    poss_meth_15_100_g_query |
    poss_meth_400_900_g_query |
    poss_meth_gte_900_g_query |
    poss_cannabis_amt_unknwn_query |
    poss_cannabis_att_amt_unknwn_query |
    poss_cannabis_lte_2pt5_g_query |
    poss_cannabis_2pt5_10_g_query |
    poss_cannabis_10_30_g_query |
    poss_cannabis_30_500_g_query |
    poss_cannabis_500_2000_g_query |
    poss_cannabis_2000_5000_g_query |
    poss_cannabis_gt_5000_g_query |
    casual_del_cannabis_2pt5_10_g_query |
    casual_del_cannabis_10_30_g_query |
    casual_del_cannabis_30_500_g_query |
    poss_cannabis_plants_5_20_query
)

# TODO: Check if felony/misdemenor classes in records line up with
# charges

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
            if ((k.startswith('mfg_del_') or k.startswith('poss_') or
                    k.startswith('casual_del')) and k.endswith('_query')):
                attr = k.replace('_query', '')
                setattr(cls, attr, filter_method_from_query(v))


class DrugQuerySetMixin(object, metaclass=DrugQuerySetMixinMeta):
    """
    QuerySet mixin that provides methods to based on charge descriptions and dispositions that represent drug crimes
    """
    # Python 3 ignores this.  Keep it here for possible backward
    # compatibility
    __metaclass__ = DrugQuerySetMixinMeta
