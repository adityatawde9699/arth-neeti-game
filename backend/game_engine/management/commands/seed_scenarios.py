"""
Management command to seed initial scenario cards.
Run with: python manage.py seed_scenarios
"""
from django.core.management.base import BaseCommand
from game_engine.models import ScenarioCard, Choice


class Command(BaseCommand):
    help = 'Seeds the database with initial scenario cards'

    def handle(self, *args, **options):
        scenarios = [
            # SOCIAL PRESSURE
            {
                'title': "Goa Trip with Friends",
                'description': "Your college friends are planning an epic trip to Goa. Everyone's going. Cost: ₹8,000.",
                'category': 'SOCIAL',
                'difficulty': 1,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Go with them! YOLO! (-₹8,000)",
                        'wealth_impact': -8000,
                        'happiness_impact': 15,
                        'credit_impact': 0,
                        'literacy_impact': -5,
                        'feedback': "Fun trip! But consider: ₹8k invested monthly in SIP for 30 years at 12% = ₹2.8 Crore!",
                        'is_recommended': False
                    },
                    {
                        'text': "Skip it and save the money",
                        'wealth_impact': 0,
                        'happiness_impact': -10,
                        'credit_impact': 0,
                        'literacy_impact': 5,
                        'feedback': "Smart move! But remember: occasional spending on experiences is important for mental health.",
                        'is_recommended': True
                    }
                ]
            },
            # WANTS
            {
                'title': "New iPhone Launch",
                'description': "The new iPhone is out! Your old phone works fine but... it's the NEW iPhone! EMI available: ₹4,000/month for 12 months.",
                'category': 'WANTS',
                'difficulty': 2,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Buy it on EMI! (-₹4,000/month debt)",
                        'wealth_impact': -4000,
                        'happiness_impact': 10,
                        'credit_impact': -20,
                        'literacy_impact': -10,
                        'feedback': "EMIs on depreciating assets = Wealth drain. Your phone loses 40% value in year 1!",
                        'is_recommended': False
                    },
                    {
                        'text': "Keep using current phone",
                        'wealth_impact': 0,
                        'happiness_impact': -5,
                        'credit_impact': 5,
                        'literacy_impact': 10,
                        'feedback': "Great decision! The 50/30/20 rule: Needs 50%, Wants 30%, Savings 20%.",
                        'is_recommended': True
                    }
                ]
            },
            # HIDDEN TRAP
            {
                'title': "Lifetime Free Credit Card",
                'description': "A smooth-talking bank agent offers a 'Lifetime Free' credit card with 5x reward points!",
                'category': 'TRAP',
                'difficulty': 3,
                'min_month': 2,
                'choices': [
                    {
                        'text': "Accept immediately! Free stuff!",
                        'wealth_impact': 0,
                        'happiness_impact': 5,
                        'credit_impact': 10,
                        'literacy_impact': -15,
                        'feedback': "Warning: 'Lifetime free' often has hidden annual fees after year 1. Always read the T&C!",
                        'is_recommended': False
                    },
                    {
                        'text': "Ask for the Terms & Conditions first",
                        'wealth_impact': 0,
                        'happiness_impact': 0,
                        'credit_impact': 5,
                        'literacy_impact': 15,
                        'feedback': "Smart! NCFE tip: Always read the fine print. Look for: Annual fees, late payment charges, and interest rates.",
                        'is_recommended': True
                    }
                ]
            },
            # NEEDS
            {
                'title': "Health Insurance Decision",
                'description': "Your company offers group health insurance (₹3L cover) but HR suggests buying personal insurance too (₹15L, costs ₹12,000/year).",
                'category': 'NEEDS',
                'difficulty': 2,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Company insurance is enough (-₹0)",
                        'wealth_impact': 0,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': -10,
                        'feedback': "Risky! If you change jobs, you lose coverage. Medical inflation in India = 14%/year!",
                        'is_recommended': False
                    },
                    {
                        'text': "Buy personal health insurance too (-₹12,000)",
                        'wealth_impact': -12000,
                        'happiness_impact': -2,
                        'credit_impact': 0,
                        'literacy_impact': 20,
                        'feedback': "Excellent! Personal insurance stays with you. Buy young = lower premiums forever.",
                        'is_recommended': True
                    }
                ]
            },
            # INVESTMENT
            {
                'title': "Start a SIP?",
                'description': "A colleague suggests starting a SIP (Systematic Investment Plan) of ₹5,000/month in a mutual fund.",
                'category': 'INVESTMENT',
                'difficulty': 1,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Start the SIP (-₹5,000/month)",
                        'wealth_impact': -5000,
                        'happiness_impact': 0,
                        'credit_impact': 5,
                        'literacy_impact': 25,
                        'feedback': "Power of Compounding! ₹5k/month for 20 years at 12% = ₹50 Lakhs! Best financial decision.",
                        'is_recommended': True
                    },
                    {
                        'text': "Maybe later, markets are volatile",
                        'wealth_impact': 0,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': -15,
                        'feedback': "Time in market > Timing the market. Starting late costs lakhs in potential gains.",
                        'is_recommended': False
                    }
                ]
            },
            # EMERGENCY
            {
                'title': "Medical Emergency",
                'description': "A family member needs ₹50,000 for a medical procedure urgently!",
                'category': 'EMERGENCY',
                'difficulty': 4,
                'min_month': 3,
                'choices': [
                    {
                        'text': "Use savings (if you have them)",
                        'wealth_impact': -50000,
                        'happiness_impact': -5,
                        'credit_impact': 0,
                        'literacy_impact': 10,
                        'feedback': "This is why emergency funds matter! Aim for 6 months of expenses saved.",
                        'is_recommended': True
                    },
                    {
                        'text': "Take a personal loan (high interest)",
                        'wealth_impact': -10000,
                        'happiness_impact': -10,
                        'credit_impact': -30,
                        'literacy_impact': -10,
                        'feedback': "Personal loan interest = 12-24%! You'll pay back ₹60,000+ over time.",
                        'is_recommended': False
                    }
                ]
            },
            # SOCIAL
            {
                'title': "Relative Asks for Loan",
                'description': "A distant relative asks to borrow ₹30,000. They promise to return it 'soon'.",
                'category': 'SOCIAL',
                'difficulty': 3,
                'min_month': 2,
                'choices': [
                    {
                        'text': "Give the loan (family is important)",
                        'wealth_impact': -30000,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': -5,
                        'feedback': "Be careful! Informal loans rarely get returned. Set clear terms and deadlines.",
                        'is_recommended': False
                    },
                    {
                        'text': "Politely decline, suggest alternatives",
                        'wealth_impact': 0,
                        'happiness_impact': -15,
                        'credit_impact': 0,
                        'literacy_impact': 10,
                        'feedback': "Relationship strain is real, but so is financial loss. Suggest formal lending options.",
                        'is_recommended': True
                    }
                ]
            },
            # TRAP - Crypto
            {
                'title': "Crypto Investment Opportunity",
                'description': "A friend says he made 10x returns on a new cryptocurrency. He's putting in ₹20,000 more. Should you?",
                'category': 'TRAP',
                'difficulty': 4,
                'min_month': 2,
                'choices': [
                    {
                        'text': "Invest ₹20,000 in crypto!",
                        'wealth_impact': -20000,
                        'happiness_impact': 10,
                        'credit_impact': 0,
                        'literacy_impact': -20,
                        'feedback': "High risk! Crypto is volatile. Only invest what you can afford to lose completely.",
                        'is_recommended': False
                    },
                    {
                        'text': "Research first, maybe invest small",
                        'wealth_impact': -2000,
                        'happiness_impact': 0,
                        'credit_impact': 0,
                        'literacy_impact': 15,
                        'feedback': "Smart! The 5% rule: Never put more than 5% of portfolio in high-risk assets.",
                        'is_recommended': True
                    }
                ]
            },
            # WANTS - Wedding
            {
                'title': "Friend's Lavish Wedding",
                'description': "Close friend's destination wedding in Udaipur. Attending costs ₹25,000 (travel, gifts, outfit).",
                'category': 'WANTS',
                'difficulty': 2,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Go all out! It's their big day! (-₹25,000)",
                        'wealth_impact': -25000,
                        'happiness_impact': 20,
                        'credit_impact': 0,
                        'literacy_impact': -5,
                        'feedback': "Social events matter, but budget for them! Create a 'celebrations fund' each year.",
                        'is_recommended': False
                    },
                    {
                        'text': "Attend but set a strict budget of ₹10,000",
                        'wealth_impact': -10000,
                        'happiness_impact': 10,
                        'credit_impact': 0,
                        'literacy_impact': 10,
                        'feedback': "Balance! You attended, maintained friendship, but didn't break the bank.",
                        'is_recommended': True
                    }
                ]
            },
            # INVESTMENT - PPF
            {
                'title': "PPF vs FD Decision",
                'description': "Tax-saving season! Should you invest ₹50,000 in PPF (locked 15 years, 7.1% tax-free) or FD (1 year, 6.5% taxable)?",
                'category': 'INVESTMENT',
                'difficulty': 2,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Invest in PPF (-₹50,000, locked)",
                        'wealth_impact': -50000,
                        'happiness_impact': -5,
                        'credit_impact': 5,
                        'literacy_impact': 20,
                        'feedback': "PPF gives EEE tax benefit (Exempt-Exempt-Exempt). Excellent for long-term wealth!",
                        'is_recommended': True
                    },
                    {
                        'text': "FD is safer, I might need the money",
                        'wealth_impact': -50000,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': 0,
                        'feedback': "FD interest is taxable at your slab. Post-tax returns often don't beat inflation.",
                        'is_recommended': False
                    }
                ]
            },
            # NEW SCENARIOS - INVESTMENT
            {
                'title': "ELSS Tax Saving Fund",
                'description': "Your CA recommends ELSS (Equity Linked Savings Scheme) for Section 80C deduction. Lock-in: 3 years. Investment: ₹50,000.",
                'category': 'INVESTMENT',
                'difficulty': 2,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Invest in ELSS (-₹50,000)",
                        'wealth_impact': -50000,
                        'happiness_impact': 0,
                        'credit_impact': 5,
                        'literacy_impact': 20,
                        'feedback': "ELSS has lowest lock-in (3 years) among 80C options. Historical returns: 12-15% CAGR!",
                        'is_recommended': True
                    },
                    {
                        'text': "Skip it, I'll manage taxes later",
                        'wealth_impact': 0,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': -10,
                        'feedback': "Missing tax deductions = paying more taxes! ₹50k in 80C saves ~₹15k in 30% bracket.",
                        'is_recommended': False
                    }
                ]
            },
            {
                'title': "NPS for Retirement",
                'description': "HR explains NPS (National Pension System) with extra ₹50k deduction under 80CCD(1B). Lock-in until 60.",
                'category': 'INVESTMENT',
                'difficulty': 3,
                'min_month': 2,
                'choices': [
                    {
                        'text': "Start NPS with ₹5,000/month",
                        'wealth_impact': -5000,
                        'happiness_impact': -5,
                        'credit_impact': 5,
                        'literacy_impact': 25,
                        'feedback': "Smart! NPS gives additional ₹50k tax deduction + low-cost fund management. Great for retirement!",
                        'is_recommended': True
                    },
                    {
                        'text': "60 is too far, I'll think later",
                        'wealth_impact': 0,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': -15,
                        'feedback': "Delaying retirement planning is costly. Starting at 25 vs 35 = 2x difference in corpus!",
                        'is_recommended': False
                    }
                ]
            },
            {
                'title': "Gold Investment Decision",
                'description': "Dhanteras is coming! Parents suggest buying gold jewellery worth ₹40,000. Alternatively, you could buy Sovereign Gold Bonds.",
                'category': 'INVESTMENT',
                'difficulty': 2,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Buy physical gold jewellery",
                        'wealth_impact': -40000,
                        'happiness_impact': 10,
                        'credit_impact': 0,
                        'literacy_impact': -5,
                        'feedback': "Jewellery has 15-20% making charges + storage risk. You lose money on resale!",
                        'is_recommended': False
                    },
                    {
                        'text': "Buy Sovereign Gold Bonds (SGB)",
                        'wealth_impact': -40000,
                        'happiness_impact': 0,
                        'credit_impact': 5,
                        'literacy_impact': 20,
                        'feedback': "SGBs give 2.5% annual interest + gold appreciation. No storage hassle, no GST on exit!",
                        'is_recommended': True
                    }
                ]
            },
            # NEW SCENARIOS - TRAPS
            {
                'title': "MLM Business Opportunity",
                'description': "An old school friend pitches a 'network marketing' opportunity. Join fee: ₹15,000. Claims: 'Make ₹1 Lakh/month passive income!'",
                'category': 'TRAP',
                'difficulty': 4,
                'min_month': 2,
                'choices': [
                    {
                        'text': "Join the network! Sounds promising!",
                        'wealth_impact': -15000,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': -25,
                        'feedback': "99% of MLM participants lose money. If income depends on recruiting, not product sales, RUN!",
                        'is_recommended': False
                    },
                    {
                        'text': "Politely decline and research first",
                        'wealth_impact': 0,
                        'happiness_impact': -5,
                        'credit_impact': 0,
                        'literacy_impact': 15,
                        'feedback': "Smart! Always research before investing. Check RBI/SEBI advisories on such schemes.",
                        'is_recommended': True
                    }
                ]
            },
            {
                'title': "Fantasy Sports Addiction",
                'description': "You've been playing Dream11/MPL daily. This week you're ₹8,000 down but feeling 'lucky' for the big match.",
                'category': 'TRAP',
                'difficulty': 4,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Put ₹5,000 more - I'll win it back!",
                        'wealth_impact': -5000,
                        'happiness_impact': -10,
                        'credit_impact': 0,
                        'literacy_impact': -20,
                        'feedback': "This is classic gambling psychology! 'Chasing losses' leads to more losses. The house always wins.",
                        'is_recommended': False
                    },
                    {
                        'text': "Stop and accept the ₹8,000 loss",
                        'wealth_impact': 0,
                        'happiness_impact': -15,
                        'credit_impact': 0,
                        'literacy_impact': 15,
                        'feedback': "Tough but wise! Recognizing gambling patterns early saves lakhs. Set strict entertainment budgets.",
                        'is_recommended': True
                    }
                ]
            },
            {
                'title': "Quick Loan App Emergency",
                'description': "You need ₹20,000 urgently. A mobile app promises 'Instant loan in 5 minutes!' Interest: 35% APR with hidden fees.",
                'category': 'TRAP',
                'difficulty': 5,
                'min_month': 3,
                'choices': [
                    {
                        'text': "Take the instant loan",
                        'wealth_impact': -7000,
                        'happiness_impact': 5,
                        'credit_impact': -40,
                        'literacy_impact': -20,
                        'feedback': "DANGER! Predatory loan apps charge 100%+ effective interest. Many are illegal. RBI has banned 600+ such apps!",
                        'is_recommended': False
                    },
                    {
                        'text': "Ask family or use credit card instead",
                        'wealth_impact': -1000,
                        'happiness_impact': -10,
                        'credit_impact': -5,
                        'literacy_impact': 10,
                        'feedback': "Credit card interest (36%) is painful but legal. Family loans are interest-free. Both better than predatory apps!",
                        'is_recommended': True
                    }
                ]
            },
            {
                'title': "Guaranteed Returns Scheme",
                'description': "A 'financial advisor' offers a scheme: 'Guaranteed 24% returns per year! Double your money in 3 years!'",
                'category': 'TRAP',
                'difficulty': 5,
                'min_month': 2,
                'choices': [
                    {
                        'text': "Invest ₹50,000 in this scheme",
                        'wealth_impact': -50000,
                        'happiness_impact': 10,
                        'credit_impact': 0,
                        'literacy_impact': -30,
                        'feedback': "SCAM ALERT! No legitimate investment guarantees 24%. This is a Ponzi scheme. Report to police!",
                        'is_recommended': False
                    },
                    {
                        'text': "Ask for SEBI registration, walk away",
                        'wealth_impact': 0,
                        'happiness_impact': 0,
                        'credit_impact': 0,
                        'literacy_impact': 25,
                        'feedback': "Perfect! Always verify SEBI registration. 'Guaranteed high returns' = 100% scam indicator.",
                        'is_recommended': True
                    }
                ]
            },
            # NEW SCENARIOS - LIFE MILESTONES
            {
                'title': "First Car Purchase",
                'description': "You're tired of commuting. A new car costs ₹8 Lakh (₹15,000/month EMI for 5 years). A good used car: ₹3.5 Lakh.",
                'category': 'WANTS',
                'difficulty': 3,
                'min_month': 4,
                'choices': [
                    {
                        'text': "Buy new car on loan",
                        'wealth_impact': -15000,
                        'happiness_impact': 20,
                        'credit_impact': -15,
                        'literacy_impact': -10,
                        'feedback': "New cars lose 20% value in year 1! Total cost with interest: ₹9.5 Lakh for ₹8 Lakh car.",
                        'is_recommended': False
                    },
                    {
                        'text': "Buy 2-3 year old certified used car",
                        'wealth_impact': -35000,
                        'happiness_impact': 10,
                        'credit_impact': 5,
                        'literacy_impact': 15,
                        'feedback': "Smart! Let someone else take the depreciation hit. Save ₹4+ Lakh for same utility!",
                        'is_recommended': True
                    }
                ]
            },
            {
                'title': "Rent vs Own Decision",
                'description': "You can rent a 2BHK for ₹20,000/month OR buy it for ₹60 Lakh (₹50,000 EMI for 20 years).",
                'category': 'NEEDS',
                'difficulty': 4,
                'min_month': 6,
                'choices': [
                    {
                        'text': "Buy the house - rent is wasted money!",
                        'wealth_impact': -50000,
                        'happiness_impact': 10,
                        'credit_impact': -20,
                        'literacy_impact': -5,
                        'feedback': "Not always true! Buy cost = ₹1.2 Cr over 20 years. Rent + invest difference often wins!",
                        'is_recommended': False
                    },
                    {
                        'text': "Rent and invest the difference",
                        'wealth_impact': -20000,
                        'happiness_impact': 0,
                        'credit_impact': 5,
                        'literacy_impact': 20,
                        'feedback': "Run the numbers! ₹30k/month SIP for 20 years at 12% = ₹3 Crore. Often beats property!",
                        'is_recommended': True
                    }
                ]
            },
            {
                'title': "Destination Wedding Pressure",
                'description': "Parents want a grand wedding (₹15 Lakh). You prefer a simple ceremony (₹3 Lakh) and investing the rest.",
                'category': 'SOCIAL',
                'difficulty': 4,
                'min_month': 5,
                'choices': [
                    {
                        'text': "Grand wedding - log kya kahenge!",
                        'wealth_impact': -150000,
                        'happiness_impact': 15,
                        'credit_impact': -10,
                        'literacy_impact': -15,
                        'feedback': "Starting marriage with debt is risky. 60% of couples regret overspending on weddings.",
                        'is_recommended': False
                    },
                    {
                        'text': "Simple wedding + ₹12 Lakh invested",
                        'wealth_impact': -30000,
                        'happiness_impact': 5,
                        'credit_impact': 10,
                        'literacy_impact': 20,
                        'feedback': "Wise! ₹12 Lakh invested today = ₹37 Lakh in 10 years. Best wedding gift to yourselves!",
                        'is_recommended': True
                    }
                ]
            },
            # NEW SCENARIOS - DIGITAL SAFETY
            {
                'title': "UPI Fraud Attempt",
                'description': "You get a call: 'Sir, your KYC is expiring. Share OTP to update.' You received an OTP just now.",
                'category': 'TRAP',
                'difficulty': 3,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Share OTP to 'help' them update",
                        'wealth_impact': -25000,
                        'happiness_impact': -30,
                        'credit_impact': -20,
                        'literacy_impact': -20,
                        'feedback': "You got scammed! Banks NEVER ask for OTP. Report immediately at cybercrime.gov.in",
                        'is_recommended': False
                    },
                    {
                        'text': "Hang up and report to bank",
                        'wealth_impact': 0,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': 20,
                        'feedback': "Perfect! Never share OTP with anyone. Banks already have your KYC - this was a scam!",
                        'is_recommended': True
                    }
                ]
            },
            {
                'title': "Phishing Email",
                'description': "Email from 'bank@secure-hdfc-update.com': 'Verify your account NOW or face suspension!' Has official logo.",
                'category': 'TRAP',
                'difficulty': 2,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Click link and enter credentials",
                        'wealth_impact': -40000,
                        'happiness_impact': -25,
                        'credit_impact': -30,
                        'literacy_impact': -15,
                        'feedback': "Phished! Always check sender domain. Banks use @hdfcbank.com NOT @secure-hdfc-update.com",
                        'is_recommended': False
                    },
                    {
                        'text': "Delete email, call official bank number",
                        'wealth_impact': 0,
                        'happiness_impact': 0,
                        'credit_impact': 0,
                        'literacy_impact': 15,
                        'feedback': "Smart! Always verify via official bank app/website. Phishing costs Indians ₹1.2 Lakh Cr/year!",
                        'is_recommended': True
                    }
                ]
            },
            # NEW SCENARIOS - SIDE HUSTLES
            {
                'title': "Freelancing Opportunity",
                'description': "A foreign client offers ₹50,000/month for weekend freelance work. Requires 15 hours/week.",
                'category': 'INVESTMENT',
                'difficulty': 2,
                'min_month': 2,
                'choices': [
                    {
                        'text': "Take the freelance gig!",
                        'wealth_impact': 50000,
                        'happiness_impact': -10,
                        'credit_impact': 5,
                        'literacy_impact': 15,
                        'feedback': "Great income boost! Remember: Freelance income is taxable. Set aside 30% for taxes.",
                        'is_recommended': True
                    },
                    {
                        'text': "Decline - weekends are for rest",
                        'wealth_impact': 0,
                        'happiness_impact': 10,
                        'credit_impact': 0,
                        'literacy_impact': 0,
                        'feedback': "Work-life balance matters! But consider: a few months of hustle can fund your emergency fund.",
                        'is_recommended': False
                    }
                ]
            },
            {
                'title': "YouTube Channel Investment",
                'description': "You want to start a YouTube channel. Need camera (₹30,000) + mic (₹5,000) + editing software (₹10,000/year).",
                'category': 'INVESTMENT',
                'difficulty': 3,
                'min_month': 3,
                'choices': [
                    {
                        'text': "Buy all equipment now",
                        'wealth_impact': -45000,
                        'happiness_impact': 15,
                        'credit_impact': 0,
                        'literacy_impact': -5,
                        'feedback': "Risky! Start with phone + free software. Only upgrade after 50+ videos to test commitment.",
                        'is_recommended': False
                    },
                    {
                        'text': "Start with phone, upgrade later",
                        'wealth_impact': -5000,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': 15,
                        'feedback': "Smart! Content > Equipment. Many successful creators started with just phones!",
                        'is_recommended': True
                    }
                ]
            },
            # NEW SCENARIOS - DAILY LIFE
            {
                'title': "Subscription Overload",
                'description': "You have Netflix (₹649), Hotstar (₹299), Prime (₹1499), Spotify (₹119), Gym (₹2000) - but use only 2 regularly.",
                'category': 'WANTS',
                'difficulty': 1,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Keep all - might use them someday",
                        'wealth_impact': -4566,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': -10,
                        'feedback': "'Subscription fatigue' costs Indians ₹5000+/month on average! Audit every 3 months.",
                        'is_recommended': False
                    },
                    {
                        'text': "Cancel unused, keep only 2",
                        'wealth_impact': -1000,
                        'happiness_impact': 0,
                        'credit_impact': 0,
                        'literacy_impact': 15,
                        'feedback': "₹3500/month saved = ₹42,000/year. That's a vacation fund! Review subscriptions quarterly.",
                        'is_recommended': True
                    }
                ]
            },
            {
                'title': "Food Delivery Habit",
                'description': "You order Swiggy/Zomato 15 times/month, spending ₹8,000. Cooking would cost ₹3,000.",
                'category': 'WANTS',
                'difficulty': 1,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Continue - too tired to cook",
                        'wealth_impact': -8000,
                        'happiness_impact': 10,
                        'credit_impact': 0,
                        'literacy_impact': -5,
                        'feedback': "₹5000/month extra = ₹60,000/year. That's a foreign trip! Also, health cost of junk food...",
                        'is_recommended': False
                    },
                    {
                        'text': "Meal prep on weekends, order 4x/month",
                        'wealth_impact': -5000,
                        'happiness_impact': 0,
                        'credit_impact': 0,
                        'literacy_impact': 10,
                        'feedback': "Balance! Occasional treats are fine. Meal prepping also improves health. Win-win!",
                        'is_recommended': True
                    }
                ]
            },
            {
                'title': "Credit Card Bill Strategy",
                'description': "Credit card bill is ₹20,000. You can pay minimum (₹1,000) or full. Cash in bank: ₹25,000.",
                'category': 'NEEDS',
                'difficulty': 2,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Pay minimum, keep cash safe",
                        'wealth_impact': -1000,
                        'happiness_impact': 5,
                        'credit_impact': -30,
                        'literacy_impact': -20,
                        'feedback': "TRAP! Credit card interest = 36-42% APR! ₹20k becomes ₹27k in a year. Always pay full!",
                        'is_recommended': False
                    },
                    {
                        'text': "Clear the full bill",
                        'wealth_impact': -20000,
                        'happiness_impact': -5,
                        'credit_impact': 15,
                        'literacy_impact': 20,
                        'feedback': "Credit card golden rule: Only spend what you can pay FULLY each month. No interest = free credit!",
                        'is_recommended': True
                    }
                ]
            },
            # NEW SCENARIOS - EMERGENCY FUND
            {
                'title': "Building Emergency Fund",
                'description': "Your monthly expense is ₹30,000. Financial advisor suggests keeping 6 months (₹1.8 Lakh) in liquid fund.",
                'category': 'INVESTMENT',
                'difficulty': 2,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Start with ₹5,000/month SIP in liquid fund",
                        'wealth_impact': -5000,
                        'happiness_impact': -5,
                        'credit_impact': 5,
                        'literacy_impact': 25,
                        'feedback': "Excellent! Emergency fund = financial peace. Liquid funds give better returns than savings account!",
                        'is_recommended': True
                    },
                    {
                        'text': "I have FDs, that's enough",
                        'wealth_impact': 0,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': -5,
                        'feedback': "FDs have premature withdrawal penalty. Liquid funds: T+1 withdrawal, better returns, no penalty!",
                        'is_recommended': False
                    }
                ]
            },
            # NEW SCENARIOS - INSURANCE
            {
                'title': "Term Insurance Decision",
                'description': "Insurance agent pushes LIC endowment (₹50k/year, returns ₹10L in 20 years). Term plan: ₹7k/year for ₹1Cr cover.",
                'category': 'NEEDS',
                'difficulty': 3,
                'min_month': 2,
                'choices': [
                    {
                        'text': "Endowment - at least I get money back!",
                        'wealth_impact': -50000,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': -15,
                        'feedback': "Endowment returns are just 4-5%! Cover is too low. You're mixing investment and insurance.",
                        'is_recommended': False
                    },
                    {
                        'text': "Term plan + invest the difference",
                        'wealth_impact': -7000,
                        'happiness_impact': 0,
                        'credit_impact': 5,
                        'literacy_impact': 25,
                        'feedback': "Golden Rule: Buy term, invest the rest! ₹43k/year in SIP for 20 years = ₹43 Lakh, not ₹10 Lakh!",
                        'is_recommended': True
                    }
                ]
            },
            {
                'title': "Laptop Theft Coverage",
                'description': "You bought a ₹80,000 laptop. Insurance offer: ₹4,000/year for theft + damage cover.",
                'category': 'NEEDS',
                'difficulty': 2,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Skip insurance - I'm careful",
                        'wealth_impact': 0,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': -5,
                        'feedback': "Laptop theft is common. If stolen, ₹80k loss vs ₹4k insurance premium. High value items need cover!",
                        'is_recommended': False
                    },
                    {
                        'text': "Get the coverage",
                        'wealth_impact': -4000,
                        'happiness_impact': -2,
                        'credit_impact': 0,
                        'literacy_impact': 10,
                        'feedback': "Smart! Insurance is for protecting against large losses you can't afford. This qualifies!",
                        'is_recommended': True
                    }
                ]
            },
            # NEW SCENARIOS - LIFESTYLE
            {
                'title': "Designer Brand Temptation",
                'description': "Sale at the mall! Nike shoes (₹12,000) you've wanted are 30% off. Current shoes are fine but 2 years old.",
                'category': 'WANTS',
                'difficulty': 1,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Buy now! Sale won't last!",
                        'wealth_impact': -8400,
                        'happiness_impact': 15,
                        'credit_impact': 0,
                        'literacy_impact': -5,
                        'feedback': "FOMO purchase! Sales are marketing tactics. If you didn't need it before sale, you don't need it now.",
                        'is_recommended': False
                    },
                    {
                        'text': "Wait, add to wishlist for 30 days",
                        'wealth_impact': 0,
                        'happiness_impact': -5,
                        'credit_impact': 0,
                        'literacy_impact': 15,
                        'feedback': "30-day rule: If you still want it after 30 days, buy it. Most impulse desires fade!",
                        'is_recommended': True
                    }
                ]
            },
            {
                'title': "Gym vs Home Workout",
                'description': "Fancy gym: ₹5,000/month with pool, sauna. Home equipment one-time: ₹15,000. You've been irregular with workouts.",
                'category': 'WANTS',
                'difficulty': 2,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Join fancy gym for motivation",
                        'wealth_impact': -5000,
                        'happiness_impact': 10,
                        'credit_impact': 0,
                        'literacy_impact': -5,
                        'feedback': "80% of gym memberships go unused after 3 months! That's ₹45k wasted. Start small.",
                        'is_recommended': False
                    },
                    {
                        'text': "Start with home workouts + YouTube",
                        'wealth_impact': -2000,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': 10,
                        'feedback': "Build the habit first, then upgrade! Many fit people work out at home for free.",
                        'is_recommended': True
                    }
                ]
            },
            {
                'title': "Birthday Party Budget",
                'description': "Best friend's birthday. Others are pitching in ₹2,000 each for an expensive restaurant. Your budget is ₹500.",
                'category': 'SOCIAL',
                'difficulty': 2,
                'min_month': 1,
                'choices': [
                    {
                        'text': "Go along - can't look cheap",
                        'wealth_impact': -2000,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': -10,
                        'feedback': "Social spending beyond means leads to stress. True friends understand budget constraints!",
                        'is_recommended': False
                    },
                    {
                        'text': "Honest conversation about budget",
                        'wealth_impact': -500,
                        'happiness_impact': -5,
                        'credit_impact': 0,
                        'literacy_impact': 15,
                        'feedback': "Boundaries are healthy! Suggest alternatives or contribute what you can. Real friends will understand.",
                        'is_recommended': True
                    }
                ]
            },
            {
                'title': "Upskilling Investment",
                'description': "A ₹25,000 online course can boost your salary by ₹10,000/month. Company won't reimburse.",
                'category': 'INVESTMENT',
                'difficulty': 2,
                'min_month': 2,
                'choices': [
                    {
                        'text': "Invest in the course",
                        'wealth_impact': -25000,
                        'happiness_impact': -5,
                        'credit_impact': 0,
                        'literacy_impact': 20,
                        'feedback': "ROI calculation: ₹25k investment → ₹1.2L/year salary increase = 480% return! Education pays.",
                        'is_recommended': True
                    },
                    {
                        'text': "Learn from free YouTube videos",
                        'wealth_impact': 0,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': 5,
                        'feedback': "Free resources are great for basics, but structured courses + certificates often accelerate careers.",
                        'is_recommended': False
                    }
                ]
            },
            # SCENARIO 35 - SOCIAL
            {
                'title': "Parents' Anniversary Gift",
                'description': "Parents' 25th anniversary coming up! Siblings suggest a ₹40,000 gold chain. Your budget is ₹10,000.",
                'category': 'SOCIAL',
                'difficulty': 2,
                'min_month': 2,
                'choices': [
                    {
                        'text': "Split equally - pay ₹20,000 share",
                        'wealth_impact': -20000,
                        'happiness_impact': 10,
                        'credit_impact': 0,
                        'literacy_impact': -10,
                        'feedback': "Overspending on gifts creates financial stress. Love isn't measured in rupees!",
                        'is_recommended': False
                    },
                    {
                        'text': "Contribute ₹10,000 + plan a home celebration",
                        'wealth_impact': -10000,
                        'happiness_impact': 15,
                        'credit_impact': 0,
                        'literacy_impact': 15,
                        'feedback': "Perfect balance! A heartfelt home party with your presence means more than expensive gifts. Communicate your budget honestly.",
                        'is_recommended': True
                    }
                ]
            },
            # SCENARIO 36 - INVESTMENT
            {
                'title': "Diwali Bonus Strategy",
                'description': "You received a ₹50,000 Diwali bonus! Options: New phone upgrade, trip to Manali, or boost your investment portfolio?",
                'category': 'INVESTMENT',
                'difficulty': 2,
                'min_month': 4,
                'choices': [
                    {
                        'text': "Celebrate! New phone + weekend trip (₹50,000)",
                        'wealth_impact': -50000,
                        'happiness_impact': 25,
                        'credit_impact': 0,
                        'literacy_impact': -15,
                        'feedback': "Bonuses feel like 'free money' but they're part of your income. Lifestyle inflation eats wealth-building potential!",
                        'is_recommended': False
                    },
                    {
                        'text': "Invest 70% (₹35k) + small treat (₹15k)",
                        'wealth_impact': -15000,
                        'happiness_impact': 10,
                        'credit_impact': 5,
                        'literacy_impact': 25,
                        'feedback': "The 70-30 bonus rule! ₹35k invested annually for 20 years at 12% = ₹28 Lakh. Celebrate wisely, build wealth smartly!",
                        'is_recommended': True
                    }
                ]
            }
            ,
            # NEW SCENARIOS - ROUND 2 EXPANSION
            {
                'title': "Unexpected Home Repair",
                'description': "Pipe burst in the bathroom! Plumber estimates repairs will cost ₹15,000 immediately.",
                'category': 'EMERGENCY',
                'difficulty': 3,
                'min_month': 3,
                'choices': [
                    {
                        'text': "Dip into Emergency Fund",
                        'wealth_impact': -15000,
                        'happiness_impact': -5,
                        'credit_impact': 0,
                        'literacy_impact': 10,
                        'feedback': "Good job! This is exactly what emergency funds are for—unplanned expenses without debt.",
                        'is_recommended': True
                    },
                    {
                        'text': "Pay using Credit Card (EMI)",
                        'wealth_impact': -16500,
                        'happiness_impact': 0,
                        'credit_impact': -5,
                        'literacy_impact': -5,
                        'feedback': "Credit works, but EMIs add interest costs. You'll pay nearly ₹1,500 extra in interest!",
                        'is_recommended': False
                    }
                ]
            },
            {
                'title': "Comfort Zone vs. Challenge",
                'description': "Offered a new role: More responsibility, slightly higher pay (+₹5k/month), but high stress. Current role is comfortable.",
                'category': 'CAREER',
                'difficulty': 2,
                'min_month': 2,
                'choices': [
                    {
                        'text': "Stay comfortable",
                        'wealth_impact': 0,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': -5,
                        'feedback': "Comfort is nice, but growth happens outside it. Early career is the time to take risks!",
                        'is_recommended': False
                    },
                    {
                        'text': "Take the challenge!",
                        'wealth_impact': 5000,
                        'happiness_impact': -5,
                        'credit_impact': 5,
                        'literacy_impact': 15,
                        'feedback': "Growth mindset! The skills you learn now will compound your earnings far more than the ₹5k raise.",
                        'is_recommended': True
                    }
                ]
            },
            {
                'title': "Co-signing a Loan",
                'description': "A close friend can't get a car loan and asks you to co-sign. They promise to pay every EMI on time.",
                'category': 'SOCIAL',
                'difficulty': 5,
                'min_month': 4,
                'choices': [
                    {
                        'text': "Co-sign to help a friend",
                        'wealth_impact': 0,
                        'happiness_impact': 10,
                        'credit_impact': -10,
                        'literacy_impact': -20,
                        'feedback': "High Risk! If they default, YOU are 100% liable. It also eats up your credit limit. Never co-sign unless you can pay it off.",
                        'is_recommended': False
                    },
                    {
                        'text': "Politely refuse",
                        'wealth_impact': 0,
                        'happiness_impact': -5,
                        'credit_impact': 0,
                        'literacy_impact': 10,
                        'feedback': "Hard but necessary. Protect your financial reputation. Co-signing is the #1 way to ruin credit scores and friendships.",
                        'is_recommended': True
                    }
                ]
            },
            {
                'title': "Last Minute Tax Panic",
                'description': "It's March! You haven't done any tax saving. Agent offers a traditional insurance policy to save tax quickly.",
                'category': 'TRAP',
                'difficulty': 3,
                'min_month': 11,
                'choices': [
                    {
                        'text': "Buy the policy to save tax",
                        'wealth_impact': -30000,
                        'happiness_impact': 5,
                        'credit_impact': 0,
                        'literacy_impact': -10,
                        'feedback': "Don't let the tax tail wag the investment dog! Bad products sold in March hurt you for years.",
                        'is_recommended': False
                    },
                    {
                        'text': "Pay the tax this year, plan better next time",
                        'wealth_impact': -10000,
                        'happiness_impact': -10,
                        'credit_impact': 0,
                        'literacy_impact': 10,
                        'feedback': "Painful but smart. Paying tax is better than locking money in a low-return product for 20 years!",
                        'is_recommended': True
                    }
                ]
            },
            {
                'title': "Lifestyle Inflation",
                'description': "You got a raise! Should you move to a bigger apartment? Rent is ₹10k higher, but it has a balcony!",
                'category': 'WANTS',
                'difficulty': 2,
                'min_month': 6,
                'choices': [
                    {
                        'text': "Upgrade! I earned it.",
                        'wealth_impact': -10000,
                        'happiness_impact': 15,
                        'credit_impact': 0,
                        'literacy_impact': -10,
                        'feedback': "Beware lifestyle creep! If spending rises with income, you never get wealthy. Keep expenses flat, invest the raise.",
                        'is_recommended': False
                    },
                    {
                        'text': "Stay put, invest the raise",
                        'wealth_impact': -2000,
                        'happiness_impact': 0,
                        'credit_impact': 5,
                        'literacy_impact': 20,
                        'feedback': "Wealth builder move! Increasing the gap between income and expense is the secret to early financial freedom.",
                        'is_recommended': True
                    }
                ]
            }
        ]

        created_count = 0
        updated_count = 0

        for scenario_data in scenarios:
            choices_data = scenario_data.pop('choices')
            
            # CHANGED: Use update_or_create instead of get_or_create
            scenario, created = ScenarioCard.objects.update_or_create(
                title=scenario_data['title'],
                defaults=scenario_data
            )
            
            # Clear existing choices to ensure idempotency (re-create them)
            # This prevents duplicate choices if we run the seed script twice
            scenario.choices.all().delete()
            
            for choice_data in choices_data:
                Choice.objects.create(card=scenario, **choice_data)

            if created:
                created_count += 1
                self.stdout.write(f"Created: {scenario.title}")
            else:
                updated_count += 1
                self.stdout.write(f"Updated: {scenario.title}")

        self.stdout.write(self.style.SUCCESS(f'\nSeeded: {created_count} new, {updated_count} updated.'))
