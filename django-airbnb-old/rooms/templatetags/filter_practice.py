from django import template

register = template.Library()


@register.filter
def w_capitals(value):
    # 만약 템플릿에서 {{ 'someting'|w_capitals}} 라면 someting이 value로 프린팅됨
    print(value)
    return value.capitalize()


# 다음과 같은 경우도 w_capitals를 이용하여 작성가능
@register.filter(name="w_capitals")
def sahndflksadfhl(value):
    return value.capitalize()
