import pytest
from app.api.schemas.user import UserCreate
from app.core.password import verify_password
from app.db.models.task import TaskRepository
from app.db.models.user import UserRepository
from app.tests.conftest import async_session_maker

test_user = UserCreate(
    username="username12",
    full_name="Full Name",
    email="email@tes12t.com",
    age=29,
    password="t3$tp@ssw0rD",
)

test_task = {'title': "Test Title", "description": "Test description", "owner_id": 1}

update_task = {'title': "Updated Title", 'description': "Updated Description", 'completed': True}


UserRepository.async_session = async_session_maker()
TaskRepository.async_session = async_session_maker()


@pytest.mark.asyncio
async def test_add_user():
    crud_result = await UserRepository.add_user(test_user.model_dump())
    assert crud_result.username == test_user.username
    assert crud_result.full_name == test_user.full_name
    assert crud_result.email == test_user.email
    assert crud_result.age == test_user.age
    assert verify_password(test_user.password, crud_result.hashed_password)
    db_result = await UserRepository.find_one(username=test_user.username)
    assert crud_result.id == db_result.id


@pytest.mark.asyncio
async def test_get_user():
    crud_result = await UserRepository.get_user_by_username(test_user.username)
    assert crud_result.username == test_user.username
    assert crud_result.full_name == test_user.full_name
    assert crud_result.email == test_user.email
    assert crud_result.age == test_user.age
    db_result = await UserRepository.find_one(username=test_user.username)
    assert crud_result.id == db_result.id


async def test_add_task():
    db_result = await UserRepository.find_one(id=1)
    test_task["owner_id"] = db_result.id
    crud_result = await TaskRepository.add_one(test_task)
    assert crud_result.title == test_task['title']
    assert crud_result.description == test_task['description']
    db_result = await TaskRepository.find_one(id=crud_result.id)
    assert crud_result.title == db_result.title


async def test_get_tasks(skip=0, limit=10):
    crud_result = await TaskRepository.find_some(offset=skip, limit=limit)
    crud_result_one = crud_result[0]
    assert crud_result_one.title == test_task['title']
    assert crud_result_one.description == test_task['description']


async def test_get_task():
    crud_result = await TaskRepository.find_one(id=1)
    assert crud_result.title == test_task['title']
    assert crud_result.description == test_task['description']
    assert crud_result.completed is False


async def test_update_task():
    crud_result = await TaskRepository.edit_one(update_task, id=1)
    assert crud_result.title == update_task['title']
    assert crud_result.description == update_task['description']
    assert crud_result.completed is update_task['completed']

    db_result = await TaskRepository.find_one(id=1)
    assert db_result.title == update_task['title']
    assert db_result.description == update_task['description']
    assert db_result.completed is update_task['completed']


async def test_delete_task():
    crud_result = await TaskRepository.delete_one(1)
    assert crud_result.title == update_task['title']
    assert crud_result.description == update_task['description']
    assert crud_result.completed is update_task['completed']

    db_result = await TaskRepository.find_one(id=1)
    assert db_result is None