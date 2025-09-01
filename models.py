from tortoise import Model, fields


class XianyuProduct(Model):
    """闲鱼商品数据模型"""

    id = fields.IntField(pk=True)
    title = fields.TextField(description="商品标题")
    price = fields.CharField(max_length=50, description="当前售价")
    area = fields.CharField(max_length=100, description="发货地区")
    seller = fields.CharField(max_length=100, description="卖家昵称")
    # 存储完整链接，不设置唯一性约束
    link = fields.TextField(description="商品链接", column_type="MEDIUMTEXT")
    # 使用 link_hash 字段保存截取后的链接 MD5 值，并设置唯一约束
    link_hash = fields.CharField(
        max_length=32, unique=True, description="商品链接哈希"
    )
    image_url = fields.TextField(
        description="商品图片链接", column_type="MEDIUMTEXT"
    )
    publish_time = fields.DatetimeField(null=True, description="发布时间")

    class Meta:
        table = "xianyu_products"

    def __str__(self):
        return f"<XianyuProduct: {self.title[:30]}...>"

    def __repr__(self):
        return f"XianyuProduct(id={self.id}, title='{self.title[:20]}...', price='{self.price}')"
