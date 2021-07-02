import inspect
from typing import Iterator


class RawRule(object):
    def __init__(self, action, subject, fields=None, conditions=None, inverted=False, reason=None):
        self.action = action
        self.subject = _subject_to_string(subject)
        self.fields = fields
        self.conditions = conditions
        self.inverted = inverted
        self.reason = reason

    def valid(self, subject, *args, **kwargs):
        if isinstance(subject, str):
            if subject != self.subject:
                return self.inverted
        else:
            if inspect.isclass(subject) and subject.__name__ != self.subject:
                return self.inverted
            if not inspect.isclass(subject) and hasattr(subject,
                                                        '__class__') and subject.__class__.__name__ != self.subject:
                return self.inverted
        if self.fields and not _matches(self.fields, subject):
            return self.inverted
        if self.conditions and not _evaluate_conditions(self.conditions, subject, *args, **kwargs):
            return self.inverted
        return not self.inverted


def _subject_to_string(value):
    if isinstance(value, str):
        return value
    elif inspect.isclass(value):
        return value.__name__
    raise ValueError('Only class or string allowed')


def _matches(fields: dict, subject):
    if subject:
        for key in fields.keys():
            if not hasattr(subject, key) or fields.get(key) != getattr(subject, key):
                return False
    else:
        return False
    return True


def _evaluate_conditions(conditions: list, subject, *args, **kwargs):
    for condition in conditions:
        if not inspect.isfunction(condition) or not condition(subject, *args, **kwargs):
            return False
    return True


def _maintain_multi_value(container, rule):
    rules = container.get(rule.action)
    if not rules:
        rules = []
        container[rule.action] = rules
    rules.append(rule)


def _evaluate_rules(rules: Iterator[RawRule], subject, *args, **kwargs):
    if rules:
        for rule in rules:
            if rule.valid(subject, *args, **kwargs):
                return True
    return False


class Ability(object):
    def __init__(self, rules):
        self.__rules = rules

    def can(self, action: str, subject, *args, **kwargs):
        rules = filter(lambda r: r.action == action, self.__rules)
        return _evaluate_rules(rules, subject, *args, **kwargs)

    def cannot(self, action: str, subject, *args, **kwargs):
        rules = filter(lambda r: r.action == action, self.__rules)
        return not _evaluate_rules(rules, subject, *args, **kwargs)


class AbilityBuilder(object):
    def __init__(self):
        self.__rules = []

    @property
    def rules(self):
        return tuple(self.__rules)

    def __append_from_subject(self, action, subject, inverted, fields, conditions, reason):
        if isinstance(subject, str) or inspect.isclass(subject):
            self.__rules.append(RawRule(action, subject, fields, conditions, inverted, reason))
        elif all(isinstance(elem, str) or inspect.isclass(elem) for elem in subject):
            for s in subject:
                self.__rules.append(RawRule(action, s, fields, conditions, inverted, reason))
        else:
            raise ValueError('The argument subject must be of type string/class or iterable of strings/classes.')

    def __append_from_action(self, action, subject, inverted, fields, conditions, reason):
        if isinstance(action, str):
            self.__append_from_subject(action, subject, inverted, fields, conditions, reason)
        elif all(isinstance(elem, str) for elem in action):
            for a in action:
                self.__append_from_subject(a, subject, inverted, fields, conditions, reason)
        else:
            raise ValueError('The argument action must be of type string or iterable of strings.')

    def can(self, action, subject, fields=None, conditions=None, reason=None):
        self.__append_from_action(action, subject, False, fields, conditions, reason)
        return self

    def cannot(self, action, subject, fields=None, conditions=None, reason=None):
        self.__append_from_action(action, subject, True, fields, conditions, reason)
        return self

    def build(self):
        return Ability(self.rules)


def define_ability(builder):
    if not inspect.isfunction(builder):
        raise ValueError('Argument must be a function.')
    ability_builder = AbilityBuilder()
    if len(inspect.signature(builder).parameters) == 1:
        builder(ability_builder.can)
    else:
        builder(ability_builder.can, ability_builder.cannot)
    return ability_builder.build()

# class FlaskAbility(object):
#     def __init__(self, app):
#         self.__app = app
#         self.__define_ability_for = None
#         if app is not None:
#             self.init_app(app)
#
#     def init_app(self, app):
#         app.before_request(self.init_abilities)
#
#     def define_for(self, f):
#         self.__define_ability_for = f
#
#     def init_abilities(self):
#         ctx = _request_ctx_stack.top
#         ability_builder = AbilityBuilder()
#         if self.__define_ability_for is not None:
#             self.__define_ability_for(ability_builder.can, ability_builder.cannot)
#         setattr(ctx, 'casl_ability', ability_builder.build())
#
#     def can(self, action, subject):
#         def wrap(f):
#             def decorated(*args, **kwargs):
#                 ctx = _request_ctx_stack.top
#                 ability = getattr(ctx, 'casl_ability')
#                 if not ability.can(action, subject):
#                     abort(403, message='Access not allowed.')
#                 return f(*args, **kwargs)
#
#             return decorated
#
#         return wrap
#
#     def cannot(self, action, subject):
#         def wrap(f):
#             def decorated(*args, **kwargs):
#                 ctx = _request_ctx_stack.top
#                 ability = getattr(ctx, 'casl_ability')
#                 if not ability.cannot(action, subject):
#                     abort(403, message='Access not allowed.')
#                 return f(*args, **kwargs)
#
#             return decorated
#
#         return wrap
