import datetime, csv
from django.contrib import admin
from .models import Order, OrderItem
from django.http import HttpResponse


def export_to_csv(modeladmin, request, queryset):
    #모델의 필드정보를 가지고 올 수 있다. 
    opts = modeladmin.model._meta
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename={}.csv'.format(opts.verbose_name)

    writer = csv.writer(response)
    # for문을 돌리지만 필드 중에서 m2m이나 one to many 필드가 아닌것만 꺼내곘다는 뜻이다.
    # 여기서 csv Header가 작성된다. 
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]

    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            # 뽑아낸 value가 datetime.datetime 형태가 맞다면
            if isinstance(value, datetime.datetime):
                value = value.strftime("%Y-%m-%d")
            data_row.append(value)
        writer.writerow(data_row)
    return response
export_to_csv.short_description = 'Export to CSV'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['product']


class OrderAdmin(admin.ModelAdmin):
    list_display = ['id','first_name','last_name', 'email','address','postal_code','city','paid', 'created','updated']
    list_filter = ['paid','created','updated']
    inlines = [OrderItemInline]
    actions = [export_to_csv]

admin.site.register(Order, OrderAdmin)