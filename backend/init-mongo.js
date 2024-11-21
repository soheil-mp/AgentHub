print('Starting MongoDB initialization...');

try {
    // Switch to admin database first
    db = db.getSiblingDB('admin');
    print('Switched to admin database');
    
    // Create root admin user if it doesn't exist
    if (!db.getUser("admin")) {
        db.createUser({
            user: "admin",
            pwd: "password123",
            roles: [{ role: "root", db: "admin" }]
        });
        print('Created admin user');
    }
    
    // Authenticate as admin
    db.auth("admin", "password123");
    print('Successfully authenticated as admin');
    
    // Create application user in admin database
    if (!db.getUser("agenthub_user")) {
        db.createUser({
            user: "agenthub_user",
            pwd: "password123",
            roles: [
                { role: "readWrite", db: "agenthub" },
                { role: "dbAdmin", db: "agenthub" }
            ]
        });
        print('Created application user');
    }

    // Switch to application database
    db = db.getSiblingDB('agenthub');
    print('Switched to agenthub database');
    
    // Create collections with validation
    const collections = {
        users: {
            validator: {
                $jsonSchema: {
                    bsonType: "object",
                    required: ["email", "created_at"],
                    properties: {
                        email: { bsonType: "string", pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$" },
                        hashed_password: { bsonType: "string" },
                        created_at: { bsonType: "date" },
                        updated_at: { bsonType: "date" }
                    }
                }
            }
        },
        conversations: {
            validator: {
                $jsonSchema: {
                    bsonType: "object",
                    required: ["user_id", "started_at"],
                    properties: {
                        user_id: { bsonType: "string" },
                        started_at: { bsonType: "date" },
                        ended_at: { bsonType: "date" },
                        metadata: { bsonType: "object" }
                    }
                }
            }
        },
        messages: {
            validator: {
                $jsonSchema: {
                    bsonType: "object",
                    required: ["conversation_id", "role", "content", "created_at"],
                    properties: {
                        conversation_id: { bsonType: "string" },
                        role: { enum: ["user", "assistant", "system"] },
                        content: { bsonType: "string" },
                        created_at: { bsonType: "date" },
                        metadata: { bsonType: "object" }
                    }
                }
            }
        },
        flight_bookings: {
            validator: {
                $jsonSchema: {
                    bsonType: "object",
                    required: ["user_id", "booking_reference", "status"],
                    properties: {
                        user_id: { bsonType: "string" },
                        booking_reference: { bsonType: "string" },
                        status: { bsonType: "string" },
                        passenger_details: { bsonType: "object" },
                        payment_status: { bsonType: "string" },
                        created_at: { bsonType: "date" },
                        updated_at: { bsonType: "date" }
                    }
                }
            }
        },
        hotel_bookings: {
            validator: {
                $jsonSchema: {
                    bsonType: "object",
                    required: ["user_id", "booking_reference", "status"],
                    properties: {
                        user_id: { bsonType: "string" },
                        booking_reference: { bsonType: "string" },
                        status: { bsonType: "string" },
                        hotel_id: { bsonType: "string" },
                        check_in_date: { bsonType: "date" },
                        check_out_date: { bsonType: "date" },
                        room_details: { bsonType: "object" },
                        guest_details: { bsonType: "object" },
                        payment_status: { bsonType: "string" },
                        created_at: { bsonType: "date" },
                        updated_at: { bsonType: "date" }
                    }
                }
            }
        },
        car_rentals: {
            validator: {
                $jsonSchema: {
                    bsonType: "object",
                    required: ["user_id", "booking_reference", "status"],
                    properties: {
                        user_id: { bsonType: "string" },
                        booking_reference: { bsonType: "string" },
                        status: { bsonType: "string" },
                        vehicle_type: { bsonType: "string" },
                        pickup_location: { bsonType: "string" },
                        dropoff_location: { bsonType: "string" },
                        pickup_time: { bsonType: "date" },
                        dropoff_time: { bsonType: "date" },
                        driver_details: { bsonType: "object" },
                        payment_status: { bsonType: "string" },
                        created_at: { bsonType: "date" },
                        updated_at: { bsonType: "date" }
                    }
                }
            }
        },
        excursions: {
            validator: {
                $jsonSchema: {
                    bsonType: "object",
                    required: ["user_id", "booking_reference", "status"],
                    properties: {
                        user_id: { bsonType: "string" },
                        booking_reference: { bsonType: "string" },
                        status: { bsonType: "string" },
                        activity_id: { bsonType: "string" },
                        activity_date: { bsonType: "date" },
                        participant_details: { bsonType: "object" },
                        payment_status: { bsonType: "string" },
                        created_at: { bsonType: "date" },
                        updated_at: { bsonType: "date" }
                    }
                }
            }
        }
    };

    // Create collections and indexes
    Object.entries(collections).forEach(([name, config]) => {
        try {
            db.createCollection(name, config);
            print(`Created collection: ${name}`);
        } catch (e) {
            if (!e.message.includes("already exists")) {
                throw e;
            }
            print(`Collection ${name} already exists`);
        }
    });

    // Create indexes
    print('Creating indexes...');
    
    // Users indexes
    db.users.createIndex({ "email": 1 }, { unique: true, background: true });
    db.users.createIndex({ "created_at": 1 }, { background: true });
    
    // Conversations indexes
    db.conversations.createIndex({ "user_id": 1, "started_at": -1 }, { background: true });
    db.conversations.createIndex({ "ended_at": 1 }, { background: true });
    
    // Messages indexes
    db.messages.createIndex({ "conversation_id": 1, "created_at": 1 }, { background: true });
    db.messages.createIndex({ "created_at": 1 }, { background: true });
    
    // Booking indexes
    db.flight_bookings.createIndex({ "user_id": 1 }, { background: true });
    db.flight_bookings.createIndex({ "booking_reference": 1 }, { unique: true, background: true });
    db.flight_bookings.createIndex({ "created_at": 1 }, { background: true });
    
    db.hotel_bookings.createIndex({ "user_id": 1 }, { background: true });
    db.hotel_bookings.createIndex({ "booking_reference": 1 }, { unique: true, background: true });
    db.hotel_bookings.createIndex({ "check_in_date": 1 }, { background: true });
    
    db.car_rentals.createIndex({ "user_id": 1 }, { background: true });
    db.car_rentals.createIndex({ "booking_reference": 1 }, { unique: true, background: true });
    db.car_rentals.createIndex({ "pickup_time": 1 }, { background: true });
    
    db.excursions.createIndex({ "user_id": 1 }, { background: true });
    db.excursions.createIndex({ "booking_reference": 1 }, { unique: true, background: true });
    db.excursions.createIndex({ "activity_date": 1 }, { background: true });
    
    print('Created all indexes');
    print('MongoDB initialization completed successfully');
} catch (error) {
    print('Error during MongoDB initialization:');
    printjson(error);
    throw error;
}
  