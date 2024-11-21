-- Users and Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User Preferences
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(id),
    preferred_currency VARCHAR(3) DEFAULT 'USD',
    preferred_language VARCHAR(5) DEFAULT 'en-US',
    notification_preferences JSONB,
    travel_preferences JSONB
);

-- Conversations and Chat History
CREATE TABLE conversations (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB
);

CREATE TABLE messages (
    id UUID PRIMARY KEY,
    conversation_id UUID REFERENCES conversations(id),
    role VARCHAR(50) NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Flight Bookings
CREATE TABLE flight_bookings (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    booking_reference VARCHAR(50) UNIQUE,
    status VARCHAR(50) NOT NULL,
    departure_airport VARCHAR(3) NOT NULL,
    arrival_airport VARCHAR(3) NOT NULL,
    departure_time TIMESTAMP WITH TIME ZONE,
    arrival_time TIMESTAMP WITH TIME ZONE,
    passenger_details JSONB,
    payment_status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Hotel Bookings
CREATE TABLE hotel_bookings (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    booking_reference VARCHAR(50) UNIQUE,
    status VARCHAR(50) NOT NULL,
    hotel_id VARCHAR(50),
    check_in_date DATE,
    check_out_date DATE,
    room_details JSONB,
    guest_details JSONB,
    payment_status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Car Rentals
CREATE TABLE car_rentals (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    booking_reference VARCHAR(50) UNIQUE,
    status VARCHAR(50) NOT NULL,
    vehicle_type VARCHAR(50),
    pickup_location VARCHAR(255),
    dropoff_location VARCHAR(255),
    pickup_time TIMESTAMP WITH TIME ZONE,
    dropoff_time TIMESTAMP WITH TIME ZONE,
    driver_details JSONB,
    payment_status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Excursions
CREATE TABLE excursions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    booking_reference VARCHAR(50) UNIQUE,
    status VARCHAR(50) NOT NULL,
    activity_id VARCHAR(50),
    activity_date DATE,
    participant_details JSONB,
    payment_status VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Sensitive Information (Encrypted)
CREATE TABLE sensitive_data (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    data_type VARCHAR(50) NOT NULL,
    encrypted_data BYTEA NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Metrics and Analytics
CREATE TABLE agent_metrics (
    id UUID PRIMARY KEY,
    agent_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER,
    success_rate FLOAT,
    error_count INTEGER,
    metadata JSONB
);

-- Indexes
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_flight_bookings_user_id ON flight_bookings(user_id);
CREATE INDEX idx_hotel_bookings_user_id ON hotel_bookings(user_id);
CREATE INDEX idx_car_rentals_user_id ON car_rentals(user_id);
CREATE INDEX idx_excursions_user_id ON excursions(user_id); 