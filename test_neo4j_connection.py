#!/usr/bin/env python3
"""
Test script to verify Neo4j Aura connection before deployment.
Run this locally to ensure your credentials are correct.
"""

import sys
from neo4j import GraphDatabase

# Neo4j Aura credentials
NEO4J_URI = "neo4j+s://28535274.databases.neo4j.io"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "hJWeWAaMXvREw8ErDMAopnsyhyDy93rgaeQi6g1B8OU"
NEO4J_DATABASE = "neo4j"


def test_connection():
    """Test the Neo4j Aura connection."""
    print("=" * 50)
    print("Neo4j Aura Connection Test")
    print("=" * 50)
    print(f"\nConnecting to: {NEO4J_URI}")
    print(f"Database: {NEO4J_DATABASE}")
    print(f"User: {NEO4J_USER}")
    print("\nAttempting connection...")

    driver = None
    try:
        # Create driver
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USER, NEO4J_PASSWORD),
            max_connection_lifetime=3600,
            max_connection_pool_size=50,
            connection_acquisition_timeout=60
        )

        # Verify connectivity
        driver.verify_connectivity()
        print("✓ Connection successful!")

        # Test query
        print("\nExecuting test query...")
        with driver.session(database=NEO4J_DATABASE) as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN count(n) as nodeCount")
            record = result.single()
            node_count = record["nodeCount"] if record else 0
            print(f"✓ Total nodes in database: {node_count}")

            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as relCount")
            record = result.single()
            rel_count = record["relCount"] if record else 0
            print(f"✓ Total relationships: {rel_count}")

            # Get node labels
            result = session.run("CALL db.labels() YIELD label RETURN label")
            labels = [record["label"] for record in result]
            print(f"\n✓ Node labels found: {len(labels)}")
            for label in labels:
                print(f"  - {label}")

        print("\n" + "=" * 50)
        print("✓ All tests passed!")
        print("=" * 50)
        print("\nYour Neo4j Aura instance is ready for deployment.")
        return True

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        print("\n" + "=" * 50)
        print("✗ Connection test failed!")
        print("=" * 50)
        print("\nTroubleshooting:")
        print("1. Check that your Neo4j Aura instance is running")
        print("2. Verify credentials in Neo4j-28535274-Created-2025-11-06.txt")
        print("3. Wait 60 seconds after instance creation")
        print("4. Check your internet connection")
        print("5. Visit: https://console.neo4j.io to verify instance status")
        return False

    finally:
        if driver:
            driver.close()
            print("\nConnection closed.")


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
