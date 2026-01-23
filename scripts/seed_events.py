#!/usr/bin/env python3
"""Script to seed the database with dummy event data."""

import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import uuid
from datetime import datetime, timedelta
import random
from app.api.v1.events.events_model import Event, BridgeState
from app.api.v1.events.events_repository import EventsRepository
from app.api.v1.state.state_service import StateService
from app.db import get_engine
from sqlmodel import SQLModel

def seed_events():
    """Create and insert 10 dummy events into the database."""
    
    # Initialize the database (create tables if they don't exist)
    # Import all models to register them with SQLModel.metadata
    from app.api.v1.events.events_repository import EventSQLModel
    from app.api.v1.state.state_repository import StateSQLModel
    from app.api.v1.admin.admin_repository import AdminUserSQLModel
    
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
    
    # Initialize repository and service
    events_repo = EventsRepository(engine)
    state_service = StateService()
    
    # Define some device IDs to simulate multiple cameras
    device_ids = ["camera_001", "camera_002", "camera_003"]
    
    # Bridge states to cycle through
    bridge_states = [
        BridgeState.CLOSED,
        BridgeState.OPENING,
        BridgeState.OPEN,
        BridgeState.OPEN,  # Stay open longer
        BridgeState.CLOSING,
        BridgeState.CLOSED,
    ]
    
    # Generate 10 events with timestamps spread over the last 24 hours
    base_time = datetime.now()
    events_created = 0
    latest_event = None
    
    print("🌱 Seeding events database...\n")
    
    for i in range(10):
        # Calculate timestamp (spread events over last 24 hours)
        minutes_ago = random.randint(0, 1440)  # 0 to 24 hours
        timestamp = base_time - timedelta(minutes=minutes_ago)
        
        # Select bridge state (cycle through states with some randomness)
        if i < len(bridge_states):
            bridge_state = bridge_states[i]
        else:
            bridge_state = random.choice(list(BridgeState))
        
        # Generate confidence (higher for OPEN/CLOSED, lower for transitional states)
        if bridge_state in [BridgeState.OPEN, BridgeState.CLOSED]:
            confidence = random.uniform(0.85, 0.99)
        elif bridge_state in [BridgeState.OPENING, BridgeState.CLOSING]:
            confidence = random.uniform(0.65, 0.85)
        else:  # UNKNOWN
            confidence = random.uniform(0.30, 0.60)
        
        # Create event
        event = Event(
            event_id=str(uuid.uuid4()),
            source_device_id=random.choice(device_ids),
            bridge_state=bridge_state,
            bridge_confidence=round(confidence, 2),
            timestamp=timestamp
        )
        
        # Save to database
        try:
            created_event = events_repo.create_event(event)
            events_created += 1
            print(f"✅ Event {events_created}/10: {created_event.bridge_state.value} "
                  f"(confidence: {created_event.bridge_confidence:.2f}) "
                  f"at {created_event.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Track the latest event (by timestamp)
            if latest_event is None or created_event.timestamp > latest_event.timestamp:
                latest_event = created_event
        except Exception as e:
            print(f"❌ Failed to create event {i+1}: {str(e)}")
    
    print(f"\n✨ Successfully created {events_created} events!")
    
    # Update state table with the latest event
    if latest_event:
        print("\n🔄 Updating state table with latest event...")
        try:
            updated_state = state_service.update_current_state(latest_event)
            print(f"✅ State updated: {updated_state.bridge_state.value} "
                  f"at {updated_state.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            print(f"❌ Failed to update state: {str(e)}")
    
    # Display summary
    print("\n📊 Summary:")
    all_events = events_repo.get_events()
    print(f"Total events in database: {len(all_events)}")
    
    # Count by state
    state_counts = {}
    for event in all_events:
        state_counts[event.bridge_state] = state_counts.get(event.bridge_state, 0) + 1
    
    print("\nEvents by state:")
    for state, count in sorted(state_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {state.value}: {count}")
    
    # Show current state
    current_state = state_service.get_current_state()
    if current_state:
        print(f"\n🎯 Current State: {current_state.bridge_state.value}")
        print(f"   Last updated: {current_state.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Last event ID: {current_state.last_event_id}")


if __name__ == "__main__":
    seed_events()

