We try to aggregate convictions based on the charge.

These are determined by a combination of the statute or the charge description for the disposition or conviciton record.


Drugs
=====

Typically statutes for these charges fall under the `Cannabis Control Act (720 ILCS 550)<http://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1937&ChapterID=53>`_ or the `Illinois Controlled Substances Act (720 ILCS 570)<http://www.ilga.gov/legislation/ilcs/ilcs3.asp?ActID=1941&ChapterID=53>`_.

Ambiguous charge descriptions
-----------------------------

When reviewing the charge descriptions, there were a number of charge descriptions where it was unclear whether or not they were drug charges or the type of drug charge that they represented. These are some notes that describe the investigation into the nature of these charges and the decision about where they should be categorized.

Weapons charges
~~~~~~~~~~~~~~~

These reflect weapons possession under the Unlawful use of a Weapon (UUW) law.

* ATT FEL POSS/UUW PRIOR
* ATT. FELON POSS. UUW

This charge description also reflects weapons possession:

* ATTEMPT FELON POSS

The corresponding statute value in the data is "720-5/8-4 (24-1.1 (A))". 720-5/8-4 means an attempted felony.  The attempt is for the value in parens, which is 720-5/24-1.1. (A).  Which is "Unlawful use of Weapons".

ATTEMPT POSS/ MISDEMEANOR
~~~~~~~~~~~~~~~~~~~~~~~~~

This has a final statute of "720-570/8-4(A)", which places it under the controlled substances act. However, when reviewing the act on the web, I couldn't find a reference to the section ""8-4(A)". Maybe this is a typo and they meant 720-5/8-4.

What this means is that we can include this charge in our count of possession-related drug charges, but we can't include it in a
numeric or drug-based breakdown.

POSS ANY SUB WITH INTENT
~~~~~~~~~~~~~~~~~~~~~~~~

Records with this charge description have two different statutes:

720-570/401.5(a-5)

        It is unlawful for any person to possess any substance with the intent to use the substance to facilitate the manufacture of any controlled substance other than methamphetamine, any counterfeit substance, or any controlled substance analog other than as authorized by this Act. 

720-570/401(C)(2)

        1 gram or more but less than 15 grams of any substance containing cocaine, or an analog thereof;

POSSESION
~~~~~~~~~

Records with this charge description have a statute of "720-550/4(F)".  Which corresponds to cannabis possession 2000-5000GR.

POSSESS 15<200 OBJECT/PAR
~~~~~~~~~~~~~~~~~~~~~~~~~

Records with this charge description have a statute of "720-570/402(A)(7)(A)(II)".  It seems to deal with LSD. 

        15 or more objects or 15 or more segregated parts of an object or objects but less than 200 objects or 200 segregated parts of an object or objects containing in them or having upon them any amount of any substance containing lysergic acid diethylamide (LSD), or an analog thereof;

Poseession with intent to deliver
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are a couple of different charge descriptions that are similar but reflect different drugs/amounts.

POSSESION WITH INTENT TO DEL

Records with this charge description have a statute of "720-570/401(C)(7.5)(I)".

        (i) 5 grams or more but less than 15 grams of  any substance listed in paragraph (1), (2), (2.1), (2.2), (3), (14.1), (19), (20), (20.1), (21), (25), or (26) of subsection (d) of Section 204, or an analog or derivative thereof

That is, schedule I drugs.

POSSESSION WITH INTENT TO DELI 

Records with this charge description have a statute of "720-570/401(C)(2)".

        1 gram or more but less than 15 grams of any substancesce containing cocaine, or an analog thereof;
POSS WITH INTENT TO DELIVER

Records with this charge description have a statute of "720-570/401(D)".

        Any person who violates this Section with regard to any other amount of a controlled or counterfeit substance containing dihydrocodeinone or dihydrocodeine or classified in Schedules I or II, or an analog thereof, which is (i) a narcotic drug, (ii) lysergic acid diethylamide (LSD) or an analog thereof, (iii) any substance containing amphetamine or fentanyl or any salt or optical isomer of amphetamine or fentanyl, or an analog thereof, or (iv) any substance containing N-Benzylpiperazine (BZP) or any salt or optical isomer of N-Benzylpiperazine (BZP), or an analog thereof, is guilty of a Class 2 felony. The fine for violation of this subsection (d) shall not be more than $200,000. 

Casual delivery of cannibis
~~~~~~~~~~~~~~~~~~~~~~~~~~~

These records have a charge descriptions like this:

* CASUAL DEL CAN/2.5 - 10 GRAMS
* CASUAL DEL CAN/10-30 GRAM/1ST
* CASUAL DEL CAN/10-30 GRAMS/2ND
* CAS DEL CAN/30-500 GRAMS/SUBQ

We'll group them with possession charges, based on the description from the relevant statute, 720-550/6:

        Any delivery of cannabis which is a casual delivery shall be treated in all respects as possession of cannabis for purposes of penalties.

Unlawful possession of cannibis
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Records reflecting charges of this type have one of the following charge descriptions, that correspond to different statutes.

UNLAWFUL POSS OF CANNABIS 

These records have a statute of 720 550/4(D).

        more than 30 grams but not more than 500 grams of any substance containing cannabisbis is guilty of a Class 4 felony; provided that if any offense under this subsection (d) is a subsequent offense, the offender shall be guilty of a Class 3 felony;


UNLAWFUL POSS.OF CANNABIS

These records have a statute of 720-550.0/4-C

        more than 10 grams but not more than 30 grams of any substance convictionsntaining cannabis is guilty of a Class A misdemeanor; provided, that if any offense under this subsection (c) is a subsequent offense, the offender shall be guilty of a Class 4 felony;

Manufacture of conterfeit substances
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Records for this crime have charge description, statute pairs like this:

* CNTRFT SUB-MAN/DEL, 56.5-1403-A
* ATT (MAN/DEL CTRFT SUB, 38-8-4(1403 3)
* ATT (MAN/DEL CTRFT SUB, 38-8-4(1403 A)

ILRS 56.5-1403-A doesn't seem to map to anything in the crosswalk that we have.
The closest match, based on the charge description seems to be ILCS 720-570/402(a), a Class 1 felony.

We'll categorize these under Class 1 Felonies

Disambiguating charges
~~~~~~~~~~~~~~~~~~~~~~

There are some cases where the charge description and statute don't line up.

We decide these cases based on some rules.

1. If the statute is more specific than the charge description, use the statute.

2. If the statute and the charge description differ, go with the charge description.  The rationale is that it is more likely that someone would mis-enter a numeric code than a human-readable description.
