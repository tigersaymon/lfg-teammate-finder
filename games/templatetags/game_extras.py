from django import template

register = template.Library()


@register.simple_tag
def get_player_profile(user, game):
    if not user.is_authenticated:
        return None
    return user.game_profiles.filter(game=game).first()