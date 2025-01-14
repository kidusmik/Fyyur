"""empty message

Revision ID: 7aaa4db170c8
Revises: 6012e70a6f96
Create Date: 2022-08-10 15:06:51.636830

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7aaa4db170c8'
down_revision = '6012e70a6f96'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('VenueGenre')
    op.drop_table('ArtistGenre')
    op.add_column('Artist', sa.Column('genres', sa.ARRAY(sa.String()), nullable=False))
    op.add_column('Venue', sa.Column('genres', sa.ARRAY(sa.String()), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genres')
    op.drop_column('Artist', 'genres')
    op.create_table('ArtistGenre',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"ArtistGenre_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('genre', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('artist_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], name='ArtistGenre_artist_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='ArtistGenre_pkey')
    )
    op.create_table('VenueGenre',
    sa.Column('id', sa.INTEGER(), server_default=sa.text('nextval(\'"VenueGenre_id_seq"\'::regclass)'), autoincrement=True, nullable=False),
    sa.Column('genre', sa.VARCHAR(length=50), autoincrement=False, nullable=True),
    sa.Column('venue_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], name='VenueGenre_venue_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='VenueGenre_pkey')
    )
    # ### end Alembic commands ###
