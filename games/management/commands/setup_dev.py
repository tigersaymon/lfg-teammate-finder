import logging
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from games.models import Game, GameRole, UserGameProfile
from lobbies.models import Lobby

User = get_user_model()


class Command(BaseCommand):
    help = 'Populates the database with initial games, roles, and test users.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Start setup_dev...'))

        # 1.
        games_data = [
            {"pk": 1, "title": "Dota 2", "slug": "dota-2", "team_size": 5,
             "icon": "games/icons/pnvleowo0axdyauzt7z7.png"},
            {"pk": 2, "title": "CS2", "slug": "cs2", "team_size": 5, "icon": "games/icons/e8iieh8poji0cbwcr92w.webp"},
            {"pk": 3, "title": "Valorant", "slug": "valorant", "team_size": 5,
             "icon": "games/icons/mcwfhyk0xewa6hmrg92z.png"},
            {"pk": 4, "title": "Overwatch 2", "slug": "overwatch-2", "team_size": 5,
             "icon": "games/icons/gxkx3hkzgtzkexugvnt2.png"},
            {"pk": 5, "title": "League of Legends", "slug": "league-of-legends", "team_size": 5,
             "icon": "games/icons/yv0p7p6vbifxwjpybr76.jpg"},
        ]

        roles_data = [
            # Dota 2 (Game PK 1)
            {"game_pk": 1, "name": "Carry", "icon": "fa-solid fa-gem", "order": 1},
            {"game_pk": 1, "name": "Mid", "icon": "fa-solid fa-wand-sparkles", "order": 2},
            {"game_pk": 1, "name": "Offlane", "icon": "fa-solid fa-shield", "order": 3},
            {"game_pk": 1, "name": "Soft Support", "icon": "fa-solid fa-hands-holding-circle", "order": 4},
            {"game_pk": 1, "name": "Hard Support", "icon": "fa-solid fa-hand-holding-heart", "order": 5},

            # CS2 (Game PK 2)
            {"game_pk": 2, "name": "Entry Fragger", "icon": "fa-solid fa-door-open", "order": 1},
            {"game_pk": 2, "name": "AWPer", "icon": "fa-solid fa-crosshairs", "order": 2},
            {"game_pk": 2, "name": "Support", "icon": "fa-solid fa-hands-holding", "order": 3},
            {"game_pk": 2, "name": "IGL", "icon": "fa-solid fa-chess-king", "order": 4},
            {"game_pk": 2, "name": "Lurker", "icon": "fa-solid fa-user-secret", "order": 5},

            # Valorant (Game PK 3)
            {"game_pk": 3, "name": "Duelist", "icon": "fa-solid fa-meteor", "order": 1},
            {"game_pk": 3, "name": "Initiator", "icon": "fa-solid fa-eye", "order": 2},
            {"game_pk": 3, "name": "Controller", "icon": "fa-solid fa-smog", "order": 3},
            {"game_pk": 3, "name": "Sentinel", "icon": "fa-solid fa-shield-halved", "order": 4},

            # Overwatch 2 (Game PK 4)
            {"game_pk": 4, "name": "Tank", "icon": "fa-solid fa-shield", "order": 1},
            {"game_pk": 4, "name": "Damage (DPS)", "icon": "fa-solid fa-gun", "order": 2},
            {"game_pk": 4, "name": "Support", "icon": "fa-solid fa-staff-snake", "order": 3},

            # LoL (Game PK 5)
            {"game_pk": 5, "name": "Top Lane", "icon": "fa-solid fa-arrow-up", "order": 1},
            {"game_pk": 5, "name": "Jungle", "icon": "fa-solid fa-tree", "order": 2},
            {"game_pk": 5, "name": "Mid Lane", "icon": "fa-solid fa-diamond", "order": 3},
            {"game_pk": 5, "name": "Bot Lane (ADC)", "icon": "fa-solid fa-crosshairs", "order": 4},
            {"game_pk": 5, "name": "Support", "icon": "fa-solid fa-hand-holding-heart", "order": 5},
        ]

        # 2. Data creation
        try:
            with transaction.atomic():
                # --- A. Create Games ---
                # mapped_games = { old_pk: Game_Instance }
                mapped_games = {}

                for g in games_data:
                    game, created = Game.objects.get_or_create(
                        slug=g['slug'],
                        defaults={
                            'title': g['title'],
                            'team_size': g['team_size'],

                            'icon': g['icon']
                        }
                    )
                    mapped_games[g['pk']] = game
                    if created:
                        self.stdout.write(f"Created Game: {game.title}")
                    else:
                        self.stdout.write(f"Game exists: {game.title}")

                # --- B. Create Roles ---
                for r in roles_data:
                    game_instance = mapped_games.get(r['game_pk'])
                    if game_instance:
                        role, created = GameRole.objects.get_or_create(
                            game=game_instance,
                            name=r['name'],
                            defaults={
                                'icon_class': r['icon'],
                                'order': r['order']
                            }
                        )
                        if created:
                            self.stdout.write(f" - Added role: {role.name}")

                # --- C. Create Users ---
                # Admin
                admin, created = User.objects.get_or_create(
                    username="admin",
                    email="admin@example.com",
                    defaults={'is_staff': True, 'is_superuser': True}
                )
                if created:
                    admin.set_password("AdminPassword1")
                    admin.save()
                    self.stdout.write(self.style.SUCCESS("Superuser created (admin/admin)"))

                # Test Player
                player, created = User.objects.get_or_create(
                    username="player1",
                    email="player1@example.com"
                )
                if created:
                    player.set_password("PlayerPassword1")
                    player.save()
                    self.stdout.write(self.style.SUCCESS("Test user created (player1/password123)"))

                # --- D. Create Profiles ---

                def ensure_profile(user, game_key, rank_name):
                    game = mapped_games.get(game_key)
                    if game:
                        UserGameProfile.objects.get_or_create(
                            user=user,
                            game=game,
                            defaults={'rank': rank_name}
                        )

                ensure_profile(admin, 1, "Immortal")  # Admin -> Dota
                ensure_profile(admin, 2, "Global Elite")  # Admin -> CS2
                ensure_profile(player, 2, "Silver 1")  # Player -> CS2

                # --- E. Create Demo Lobby ---
                cs2_game = mapped_games.get(2)  # CS2
                if cs2_game:
                    if not Lobby.objects.filter(title="Test Lobby for Review").exists():
                        Lobby.objects.create(
                            title="Test Lobby for Review",
                            description="Auto-generated lobby to show functionality.",
                            game=cs2_game,
                            host=player,  # player1 is host
                            size=5,
                            is_public=True
                        )
                        self.stdout.write(self.style.SUCCESS("Demo Lobby created!"))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during setup: {e}"))
            raise e

        self.stdout.write(self.style.SUCCESS('DONE! Setup complete.'))