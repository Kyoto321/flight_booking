from django.core.management.base import BaseCommand
from apps.airlines.models import Airline, Airport, Route


class Command(BaseCommand):
    help = "Seed airlines, airports, and routes (production-ready dataset)"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Seeding airlines and airports..."))

        # --------------------------------------------------
        # AIRLINES
        # --------------------------------------------------
        airlines_data = [
            {"name": "Air Peace", "code": "P4", "priority": 1},
            {"name": "Ibom Air", "code": "QI", "priority": 2},
            {"name": "Arik Air", "code": "W3", "priority": 3},
            {"name": "Aero Contractors", "code": "N2", "priority": 4},
            {"name": "Max Air", "code": "VM", "priority": 5},
        ]

        airlines = {}

        for data in airlines_data:
            airline, _ = Airline.objects.update_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "priority": data["priority"],
                    "is_active": True,
                    "search_enabled": True,
                },
            )
            airlines[data["code"]] = airline

        self.stdout.write(self.style.SUCCESS("Airlines seeded"))

        # --------------------------------------------------
        # AIRPORTS (SEARCHABLE + NON-SEARCHABLE)
        # --------------------------------------------------
        airports_data = [
            # --- HIGH PRIORITY (SEARCHABLE) ---
            {"city": "Lagos", "name": "Murtala Muhammed International Airport", "iata": "LOS", "state": "Lagos", "searchable": True},
            {"city": "Abuja", "name": "Nnamdi Azikiwe International Airport", "iata": "ABV", "state": "FCT", "searchable": True},
            {"city": "Port Harcourt", "name": "Port Harcourt International Airport", "iata": "PHC", "state": "Rivers", "searchable": True},
            {"city": "Kano", "name": "Mallam Aminu Kano International Airport", "iata": "KAN", "state": "Kano", "searchable": True},
            {"city": "Uyo", "name": "Victor Attah International Airport", "iata": "UYO", "state": "Akwa Ibom", "searchable": True},
            {"city": "Enugu", "name": "Akanu Ibiam International Airport", "iata": "ENU", "state": "Enugu", "searchable": True},
            {"city": "Benin", "name": "Benin Airport", "iata": "BNI", "state": "Edo", "searchable": True},
            {"city": "Owerri", "name": "Sam Mbakwe Airport", "iata": "QOW", "state": "Imo", "searchable": True},
            {"city": "Ilorin", "name": "Ilorin International Airport", "iata": "ILR", "state": "Kwara", "searchable": True},

            # --- SECONDARY (LIMITED FLIGHTS) ---
            {"city": "Calabar", "name": "Margaret Ekpo International Airport", "iata": "CBQ", "state": "Cross River", "searchable": True},
            {"city": "Yola", "name": "Yola Airport", "iata": "YOL", "state": "Adamawa", "searchable": True},
            {"city": "Jos", "name": "Yakubu Gowon Airport", "iata": "JOS", "state": "Plateau", "searchable": True},
            {"city": "Maiduguri", "name": "Maiduguri Airport", "iata": "MIU", "state": "Borno", "searchable": True},

            # --- NON-SEARCHABLE (FUTURE / LOW TRAFFIC) ---
            {"city": "Ibadan", "name": "Ibadan Airport", "iata": "IBA", "state": "Oyo", "searchable": False},
            {"city": "Warri", "name": "Osubi Airport", "iata": "QRW", "state": "Delta", "searchable": False},
            {"city": "Akure", "name": "Akure Airport", "iata": "AKR", "state": "Ondo", "searchable": False},
        ]

        airports = {}

        for data in airports_data:
            airport, _ = Airport.objects.update_or_create(
                iata_code=data["iata"],
                defaults={
                    "name": data["name"],
                    "city": data["city"],
                    "state": data["state"],
                    "is_active": True,
                    "is_searchable": data["searchable"],
                },
            )
            airports[data["iata"]] = airport

        self.stdout.write(self.style.SUCCESS("Airports seeded"))

        # --------------------------------------------------
        # ROUTES (REALISTIC HIGH-DEMAND)
        # --------------------------------------------------
        routes_data = [
            # Lagos ↔ Abuja
            ("P4", "LOS", "ABV"), ("P4", "ABV", "LOS"),
            ("W3", "LOS", "ABV"), ("QI", "LOS", "ABV"),

            # Lagos ↔ PHC
            ("P4", "LOS", "PHC"), ("P4", "PHC", "LOS"),
            ("N2", "LOS", "PHC"),

            # Lagos ↔ Uyo
            ("QI", "LOS", "UYO"), ("QI", "UYO", "LOS"),

            # Abuja ↔ Kano
            ("VM", "KAN", "ABV"), ("VM", "ABV", "KAN"),

            # Lagos ↔ Enugu
            ("P4", "LOS", "ENU"), ("P4", "ENU", "LOS"),
        ]

        for airline_code, from_code, to_code in routes_data:
            if airline_code in airlines and from_code in airports and to_code in airports:
                Route.objects.update_or_create(
                    airline=airlines[airline_code],
                    from_airport=airports[from_code],
                    to_airport=airports[to_code],
                    defaults={"is_active": True},
                )

        self.stdout.write(self.style.SUCCESS("Routes seeded"))

        self.stdout.write(self.style.SUCCESS("Seeding completed successfully 🚀"))