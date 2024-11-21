Write-Host "Checking MongoDB users and permissions..."

# Check admin database users
Write-Host "`n=== Admin Database Users ==="
docker exec backend-mongodb-1 mongosh --eval @'
    const users = db.getSiblingDB('admin').getUsers();
    users.users.forEach(user => {
        print(`\nUser: ${user.user}`);
        print(`Database: ${user.db}`);
        print('Roles:');
        user.roles.forEach(role => print(`  - ${role.role} on ${role.db}`));
    });
'@ "mongodb://admin:password123@localhost:27017/admin"

# Check application database users
Write-Host "`n=== Application Database Users ==="
docker exec backend-mongodb-1 mongosh --eval @'
    const users = db.getSiblingDB('agenthub').getUsers();
    if (users.users && users.users.length > 0) {
        users.users.forEach(user => {
            print(`\nUser: ${user.user}`);
            print(`Database: ${user.db}`);
            print('Roles:');
            user.roles.forEach(role => print(`  - ${role.role} on ${role.db}`));
        });
    } else {
        print('No users defined directly in agenthub database');
    }
'@ "mongodb://admin:password123@localhost:27017/admin"

# Check user permissions
Write-Host "`n=== User Permissions ==="
docker exec backend-mongodb-1 mongosh --eval @'
    const user = db.getSiblingDB('admin').runCommand({
        usersInfo: { user: "agenthub_user", db: "admin" },
        showPrivileges: true
    }).users[0];

    print(`\nUser: ${user.user}`);
    print('\nRoles:');
    user.roles.forEach(role => print(`  - ${role.role} on ${role.db}`));
    
    print('\nInherited Privileges:');
    user.inheritedPrivileges.forEach(priv => {
        const resource = priv.resource.collection 
            ? `${priv.resource.db}.${priv.resource.collection}`
            : priv.resource.db;
        print(`\n  Resource: ${resource}`);
        print('  Actions:');
        priv.actions.forEach(action => print(`    - ${action}`));
    });
'@ "mongodb://admin:password123@localhost:27017/admin" 