#!/usr/bin/env python3
"""
Verify Railway database setup for EmotiCare
"""

import os
import sys

def check_environment_variables():
    """Check if all required environment variables are set"""
    print("🔍 Checking Environment Variables")
    print("=" * 40)
    
    required_vars = {
        'DATABASE_URL': 'PostgreSQL connection string',
        'REDIS_URL': 'Redis connection string',
        'USE_POSTGRES': 'Enable PostgreSQL usage',
        'SECRET_KEY': 'Flask secret key',
        'GROQ_API_KEY': 'Groq AI API key'
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            if var in ['DATABASE_URL', 'REDIS_URL', 'SECRET_KEY', 'GROQ_API_KEY']:
                print(f"✅ {var}: {value[:20]}... ({description})")
            else:
                print(f"✅ {var}: {value} ({description})")
        else:
            print(f"❌ {var}: Not set ({description})")
            missing_vars.append(var)
    
    return len(missing_vars) == 0

def test_postgresql_connection():
    """Test PostgreSQL database connection"""
    print("\n🐘 Testing PostgreSQL Connection")
    print("=" * 40)
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        # Parse the database URL
        parsed = urlparse(database_url)
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            host=parsed.hostname,
            port=parsed.port,
            database=parsed.path[1:],  # Remove leading slash
            user=parsed.username,
            password=parsed.password
        )
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print(f"✅ PostgreSQL connected successfully")
        print(f"📊 Version: {version}")
        
        # Check if tables exist
        cursor.execute("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        tables = cursor.fetchall()
        
        if tables:
            print(f"📋 Tables found: {len(tables)}")
            for table in tables:
                print(f"   - {table[0]}")
        else:
            print("📋 No tables found (will be created on first run)")
        
        cursor.close()
        conn.close()
        return True
        
    except ImportError:
        print("❌ psycopg2 not installed")
        return False
    except Exception as e:
        print(f"❌ PostgreSQL connection failed: {e}")
        return False

def test_redis_connection():
    """Test Redis database connection"""
    print("\n🔴 Testing Redis Connection")
    print("=" * 40)
    
    redis_url = os.getenv('REDIS_URL')
    if not redis_url:
        print("❌ REDIS_URL not found")
        return False
    
    try:
        import redis
        
        # Connect to Redis
        r = redis.from_url(redis_url)
        
        # Test connection
        r.ping()
        print("✅ Redis connected successfully")
        
        # Test basic operations
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        r.delete('test_key')
        
        print(f"✅ Redis operations working")
        
        # Get Redis info
        info = r.info()
        print(f"📊 Redis version: {info.get('redis_version', 'Unknown')}")
        print(f"📊 Memory usage: {info.get('used_memory_human', 'Unknown')}")
        
        return True
        
    except ImportError:
        print("❌ redis library not installed")
        return False
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def test_flask_app_database():
    """Test Flask app database configuration"""
    print("\n🌐 Testing Flask App Database Configuration")
    print("=" * 40)
    
    try:
        # Import your Flask app
        from app import create_app
        
        app = create_app()
        
        with app.app_context():
            # Check SQLAlchemy configuration
            db_uri = app.config.get('SQLALCHEMY_DATABASE_URI')
            if db_uri:
                if 'postgresql' in db_uri:
                    print("✅ Flask configured for PostgreSQL")
                else:
                    print("⚠️ Flask not using PostgreSQL")
            else:
                print("❌ No database URI configured")
            
            # Check Redis session configuration
            session_type = app.config.get('SESSION_TYPE')
            if session_type == 'redis':
                print("✅ Flask configured for Redis sessions")
            else:
                print("⚠️ Flask not using Redis sessions")
            
            return True
            
    except Exception as e:
        print(f"❌ Flask app test failed: {e}")
        return False

def main():
    """Run all database verification tests"""
    print("🗄️ Railway Database Setup Verification")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", check_environment_variables),
        ("PostgreSQL Connection", test_postgresql_connection),
        ("Redis Connection", test_redis_connection),
        ("Flask App Configuration", test_flask_app_database)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n📊 Verification Summary")
    print("=" * 30)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All database tests passed!")
        print("✅ Your EmotiCare app is ready for production!")
    else:
        print("\n⚠️ Some tests failed. Check the Railway setup:")
        print("💡 1. Add PostgreSQL database in Railway")
        print("💡 2. Add Redis database in Railway") 
        print("💡 3. Set environment variables in Railway")
        print("💡 4. Restart your application")

if __name__ == "__main__":
    main()
