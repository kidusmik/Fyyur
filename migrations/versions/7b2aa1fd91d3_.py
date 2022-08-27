"""empty message

Revision ID: 7b2aa1fd91d3
Revises: e351838b302e
Create Date: 2022-08-12 10:10:50.626653

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b2aa1fd91d3'
down_revision = 'e351838b302e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Artist', 'past_shows_count',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('Artist', 'upcoming_shows_count',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.add_column('Show', sa.Column('venue_image_link', sa.String(length=500), nullable=False))
    op.add_column('Show', sa.Column('artist_image_link', sa.String(length=500), nullable=False))
    op.alter_column('Venue', 'past_shows_count',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('Venue', 'upcoming_shows_count',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('Venue', 'upcoming_shows_count',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('Venue', 'past_shows_count',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('Show', 'artist_image_link')
    op.drop_column('Show', 'venue_image_link')
    op.alter_column('Artist', 'upcoming_shows_count',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('Artist', 'past_shows_count',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
