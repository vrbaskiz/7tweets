import abc
import pg8000
from seventweets.config import Config


class Migration(metaclass=abc.ABCMeta):
    """
    Base class for all migrations. It is used to define common interface for
    all migrations that `MigrationManager` knows how to use and as a way to
    discover all migrations (all subclasses of this class).
    """

    @abc.abstractmethod
    def id(self):
        """
        All migrations have to have unique ID. This methods returns it.
        
        IDs have to be integers and IDs have to be incremented in comparison
        to previous migrations since this ID is used to determine which
        migrations are applied and which are not.
        """
        pass

    @abc.abstractmethod
    def upgrade(self, cursor):
        """
        Performs operations on database to upgrade current schema.
        :param cursor: Database cursor.
        """
        pass

    @abc.abstractmethod
    def downgrade(self, cursor):
        """
        Performs operations on database to downgrade current schema.
        :param cursor: Database cursor. 
        """
        pass


class InitialMigration(Migration):
    """
    Migration that creates initial tables for seventweets.
    """
    def id(self):
        return 1

    def upgrade(self, cursor):
        cursor.execute('''
            CREATE TABLE tweets (
            id SERIAL PRIMARY KEY,
            name VARCHAR(20) NOT NULL,
            tweet TEXT);
        ''')

    def downgrade(self, cursor):
        cursor.execute('''
            DROP TABLE tweets;
        ''')


class MigrationManager:
    """
    This class manages migrations and performs upgrade and downgrade actions.
    
    Migration is defined as class that inherits `Migration` base class and 
    implements its abstracts methods. All migrations must have implemented 
    `id()` method that returns integer higher that previous migrations.
    
    If direction for migrations is 'upgrade', all will be performed
    If direction for migrations is 'downgrade' only one will be performed. This
    is done for safety and since generally downgrade migrations are not very
    often and are destructive.
    """
    UP = 'up'
    DOWN = 'down'

    def __init__(self, version_table='_migrations'):
        """
        :param version_table: Name of table to hold current migration status. 
        """
        self.version_table = version_table
        self.db = pg8000.connect(**Config.DB_CONFIG)
        self.ensure_infrastructure()
        self.migrations = self.collect_migrations()

    @staticmethod
    def collect_migrations():
        """
        Collects and returns all migrations that could be found.
        
        Migrations will be found if they inherit `Migrations` class. Also, note
        that module where migrations are defined needs to be executed in order
        for `__subclasses__` method to work.
        """
        migrations = [cls() for cls in Migration.__subclasses__()]
        return sorted(migrations, key=lambda migration: migration.id())

    def migrate(self, direction):
        """
        Executes migrations.
        
        In case of 'upgrade' migrations, all unapplied will be applied.
        In case of 'downgrade' migration, only one will be applied.
        :param direction: 
            Either `MigrationManager.UP` or `MigrationManager.DOWN`.
        """
        if direction not in [self.UP, self.DOWN]:
            raise ValueError(f'Invalid direction: {direction}')
        if direction == self.UP:
            self._upgrade()
        else:
            self._downgrade()

    def _upgrade(self):
        current_version = self.current_version()

        for migration in self.migrations:
            if migration.id() > current_version:
                cursor = self.db.cursor()
                try:
                    migration.upgrade(cursor)
                    self.db.commit()
                except:
                    self.db.rollback()
                    raise
                else:
                    self.set_version(migration.id())
                finally:
                    cursor.close()

    def _downgrade(self):
        current_version = self.current_version()
        current_index = -1
        for i, migrations in enumerate(self.migrations):
            if migrations.id() == current_version:
                current_index = i

        cursor = self.db.cursor()
        try:
            self.migrations[current_index].downgrade(cursor)
            self.db.commit()
        except:
            self.db.rollback()
            raise
        else:
            if current_index == 0:
                self.set_version(0)
            else:
                prev_migration = self.migrations[current_index-1]
                self.set_version(prev_migration.id())
        finally:
            cursor.close()

    def ensure_infrastructure(self):
        """
        Makes sure that table for tracking migration exists in database.
        """
        cur = self.db.cursor()
        cur.execute(f'''
            CREATE TABLE IF NOT EXISTS {self.version_table}
            (
                version integer
            );
        ''')
        self.db.commit()
        cur.close()

    def current_version(self):
        """
        Returns currently applied migration from database.
        """
        cur = self.db.cursor()
        cur.execute(f'''
            SELECT version FROM {self.version_table} LIMIT 1;
        ''')
        cur_version = cur.fetchone()
        if cur_version is None:
            version = 0
        else:
            version = cur_version[0]

        cur.close()
        return version

    def set_version(self, version):
        """
        Sets version to migration table in database.
        :param version: Version to set.
        """
        cur = self.db.cursor()
        cur.execute(f'''
            SELECT count(*) FROM {self.version_table};
        ''')
        count = cur.fetchone()[0]
        if count == 0:
            cur.execute(f'''
                INSERT INTO {self.version_table} (version) VALUES (%s);
            ''', (version, ))
        else:
            cur.execute(f'''
                UPDATE {self.version_table} SET version=%s;
            ''', (version, ))
        self.db.commit()
        cur.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.db.close()

    def __del__(self):
        """
        If object is out of scope, we want to
        :return:
        """
        try:
            self.db.close()
        except pg8000.core.InterfaceError:
            # this exception is raised if db is already closed, which will
            # happen if class is used as context manager
            pass


def migrate(direction):
    """
    Performs all migrations that are not applied to database.
    :param direction: Either 'up' or 'down'.
    """
    with MigrationManager() as migrations:
        migrations.migrate(direction)
