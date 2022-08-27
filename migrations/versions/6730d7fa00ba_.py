"""empty message

Revision ID: 6730d7fa00ba
Revises: 76fffb59cb89
Create Date: 2022-08-15 13:05:14.597495

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6730d7fa00ba'
down_revision = '76fffb59cb89'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Show', 'venue_image_link')
    op.drop_column('Show', 'artist_name')
    op.drop_column('Show', 'venue_name')
    op.drop_column('Show', 'artist_image_link')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Show', sa.Column('artist_image_link', sa.VARCHAR(length=500), autoincrement=False, nullable=False))
    op.add_column('Show', sa.Column('venue_name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('Show', sa.Column('artist_name', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.add_column('Show', sa.Column('venue_image_link', sa.VARCHAR(length=500), autoincrement=False, nullable=False))
    # ### end Alembic commands ###