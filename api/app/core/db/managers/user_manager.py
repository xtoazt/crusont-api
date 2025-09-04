import secrets
import time
from typing import Dict, Any, Optional, List
from motor.motor_asyncio import AsyncIOMotorClient
from ..exceptions import DatabaseError
from ...config import Settings

settings = Settings()

class UserDatabase:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.db_url)
        self.collection = self.client['db']['users']
        self.api_keys_collection = self.client['db']['api_keys']

class UserManager:
    def __init__(self):
        self.db = UserDatabase()

    async def get_user(
        self,
        user_id: Optional[int] = None,
        key: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        try:
            if key:
                # First check if this is an API key
                api_key_doc = await self.db.api_keys_collection.find_one({'key': key})
                if api_key_doc:
                    # Get the user associated with this API key
                    user = await self.db.collection.find_one({'user_id': api_key_doc['user_id']})
                    if user:
                        # Add API key info to user data
                        user['api_key_id'] = api_key_doc['_id']
                        user['api_key_name'] = api_key_doc.get('name', 'Unnamed Key')
                        return user
                return None
            else:
                query = {'user_id': user_id}
                return await self.db.collection.find_one(query)
        except Exception as e:
            raise DatabaseError(f'Failed to retrieve user: {str(e)}')

    async def update_user(
        self,
        user_id: str,
        new_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        try:
            update_data = {k: v for k, v in new_data.items() if k != '_id'}
            
            return await self.db.collection.update_one(
                filter={'user_id': user_id},
                update={'$set': update_data}
            )

        except Exception as e:
            raise DatabaseError(f'Failed to update user: {str(e)}')

    async def create_api_key(
        self,
        user_id: str,
        name: str = "Default Key"
    ) -> Dict[str, Any]:
        """Create a new API key for a user"""
        try:
            key = f'cr-{secrets.token_hex(16)}'
            api_key_doc = {
                'user_id': user_id,
                'key': key,
                'name': name,
                'created_at': time.time(),
                'last_used': None,
                'is_active': True
            }
            result = await self.db.api_keys_collection.insert_one(api_key_doc)
            api_key_doc['_id'] = result.inserted_id
            return api_key_doc
        except Exception as e:
            raise DatabaseError(f'Failed to create API key: {str(e)}')

    async def get_user_api_keys(
        self,
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Get all API keys for a user"""
        try:
            cursor = self.db.api_keys_collection.find({'user_id': user_id, 'is_active': True})
            return await cursor.to_list(length=None)
        except Exception as e:
            raise DatabaseError(f'Failed to retrieve API keys: {str(e)}')

    async def delete_api_key(
        self,
        user_id: str,
        key_id: str
    ) -> bool:
        """Delete (deactivate) an API key"""
        try:
            result = await self.db.api_keys_collection.update_one(
                {'_id': key_id, 'user_id': user_id},
                {'$set': {'is_active': False}}
            )
            return result.modified_count > 0
        except Exception as e:
            raise DatabaseError(f'Failed to delete API key: {str(e)}')

    async def update_api_key_last_used(
        self,
        key: str
    ) -> None:
        """Update the last used timestamp for an API key"""
        try:
            await self.db.api_keys_collection.update_one(
                {'key': key},
                {'$set': {'last_used': time.time()}}
            )
        except Exception as e:
            # Don't raise error for this, just log it
            print(f'Failed to update API key last used: {str(e)}')