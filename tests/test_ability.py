from casl import Ability, RawRule, define_ability


class TestUser(object):

    def __init__(self, year):
        self.year = year


class Article(object):

    def __init__(self, title, author=None, published=False):
        self.title = title
        self.author = author
        self.published = published


def test_rule_validation():
    rule = RawRule(None, 'Test')
    assert rule.valid('Test') is True
    assert rule.valid('NoTest') is False

    rule = RawRule(None, 'TestUser', {'year': 43})
    assert rule.valid(TestUser(34)) is False
    assert rule.valid(TestUser(43)) is True

    rule = RawRule(None, 'TestUser', conditions=[lambda u: u.year <= 43])
    assert rule.valid(TestUser(25)) is True
    assert rule.valid(TestUser(43)) is True
    assert rule.valid(TestUser(44)) is False

    rule = RawRule(None, 'TestUser', {'year': 43}, inverted=True)
    assert rule.valid(TestUser(34)) is True
    assert rule.valid(TestUser(43)) is False

    rule = RawRule(None, 'TestUser', conditions=[lambda u: u.year <= 43], inverted=True)
    assert rule.valid(TestUser(25)) is False
    assert rule.valid(TestUser(43)) is False
    assert rule.valid(TestUser(44)) is True


def test_ability_can():
    ability = define_ability(lambda can: can('read', Article).can('write', 'Article'))
    assert isinstance(ability, Ability)

    assert ability.can('read', Article) is True
    assert ability.can('read', 'Article') is True
    assert ability.can('read', 'NoArticle') is False
    assert ability.can('read', TestUser) is False

    assert ability.can('write', Article) is True
    assert ability.can('write', 'Article') is True
    assert ability.can('write', 'NoArticle') is False
    assert ability.can('write', TestUser) is False


def test_ability_cannot():
    ability = define_ability(lambda can, cannot: cannot('write', Article).can('read', 'Article'))
    assert isinstance(ability, Ability)

    assert ability.can('read', Article) is True
    assert ability.can('write', Article) is False
    assert ability.cannot('read', Article) is False
    assert ability.cannot('write', Article) is True


def test_ability_fields():
    ability = define_ability(
        lambda can: can('read', Article, fields={'published': True}).can('write', Article,
                                                                         fields={'author': 'TestUser'}))
    assert ability.can('read', Article('CASL', published=True)) is True
    assert ability.can('read', Article('CASL')) is False
    assert ability.can('write', Article('CASL', 'TestUser')) is True
    assert ability.can('write', Article('CASL', 'NoTestUser')) is False


def test_ability_multi_action():
    ability = define_ability(
        lambda can: can(['read', 'write'], Article))

    assert ability.can('read', Article) is True
    assert ability.can('write', Article) is True


def test_ability_multi_subject():
    ability = define_ability(
        lambda can: can('read', [Article, TestUser]))

    assert ability.can('read', Article) is True
    assert ability.can('read', TestUser) is True


def test_ability_multi_action_subject():
    ability = define_ability(
        lambda can: can(['read', 'write'], [Article, TestUser]))

    assert ability.can('read', Article) is True
    assert ability.can('write', Article) is True
    assert ability.can('read', TestUser) is True
    assert ability.can('write', TestUser) is True
