"use client";

import { useState } from "react";
import { updateUserAction, deleteUserAction } from "@/actions/admin-users-action";

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  date_joined: string;
  last_login: string | null;
}

interface UsersTableProps {
  initialUsers: User[];
}

export function UsersTable({ initialUsers }: UsersTableProps) {
  const [users, setUsers] = useState<User[]>(initialUsers);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editData, setEditData] = useState<Partial<User>>({});

  const handleEdit = (user: User) => {
    setEditingId(user.id);
    setEditData({
      username: user.username,
      email: user.email,
      first_name: user.first_name,
      last_name: user.last_name,
      is_active: user.is_active,
      is_staff: user.is_staff,
      is_superuser: user.is_superuser,
    });
  };

  const handleSave = async (userId: number) => {
    const result = await updateUserAction(userId, editData);
    if (result.success) {
      setUsers(
        users.map((u) => (u.id === userId ? { ...u, ...editData } : u))
      );
      setEditingId(null);
    } else {
      alert(result.error);
    }
  };

  const handleDelete = async (userId: number) => {
    if (!confirm("Are you sure you want to delete this user?")) return;

    const result = await deleteUserAction(userId);
    if (result.success) {
      setUsers(users.filter((u) => u.id !== userId));
    } else {
      alert(result.error);
    }
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              ID
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Username
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Email
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Name
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Status
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Roles
            </th>
            <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Actions
            </th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {users.map((user) => (
            <tr key={user.id}>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {user.id}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {editingId === user.id ? (
                  <input
                    type="text"
                    value={editData.username}
                    onChange={(e) =>
                      setEditData({ ...editData, username: e.target.value })
                    }
                    className="border rounded px-2 py-1"
                  />
                ) : (
                  user.username
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {editingId === user.id ? (
                  <input
                    type="email"
                    value={editData.email}
                    onChange={(e) =>
                      setEditData({ ...editData, email: e.target.value })
                    }
                    className="border rounded px-2 py-1"
                  />
                ) : (
                  user.email
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {editingId === user.id ? (
                  <div className="flex gap-1">
                    <input
                      type="text"
                      value={editData.first_name}
                      onChange={(e) =>
                        setEditData({ ...editData, first_name: e.target.value })
                      }
                      placeholder="First"
                      className="border rounded px-2 py-1 w-20"
                    />
                    <input
                      type="text"
                      value={editData.last_name}
                      onChange={(e) =>
                        setEditData({ ...editData, last_name: e.target.value })
                      }
                      placeholder="Last"
                      className="border rounded px-2 py-1 w-20"
                    />
                  </div>
                ) : (
                  `${user.first_name} ${user.last_name}`.trim() || "-"
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap">
                {editingId === user.id ? (
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={editData.is_active}
                      onChange={(e) =>
                        setEditData({ ...editData, is_active: e.target.checked })
                      }
                      className="mr-2"
                    />
                    Active
                  </label>
                ) : (
                  <span
                    className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                      user.is_active
                        ? "bg-green-100 text-green-800"
                        : "bg-red-100 text-red-800"
                    }`}
                  >
                    {user.is_active ? "Active" : "Inactive"}
                  </span>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {editingId === user.id ? (
                  <div className="flex flex-col gap-1">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={editData.is_staff}
                        onChange={(e) =>
                          setEditData({ ...editData, is_staff: e.target.checked })
                        }
                        className="mr-2"
                      />
                      Staff
                    </label>
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={editData.is_superuser}
                        onChange={(e) =>
                          setEditData({
                            ...editData,
                            is_superuser: e.target.checked,
                          })
                        }
                        className="mr-2"
                      />
                      Superuser
                    </label>
                  </div>
                ) : (
                  <div className="flex gap-2">
                    {user.is_superuser && (
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800">
                        Superuser
                      </span>
                    )}
                    {user.is_staff && (
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        Staff
                      </span>
                    )}
                  </div>
                )}
              </td>
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                {editingId === user.id ? (
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleSave(user.id)}
                      className="text-green-600 hover:text-green-900"
                    >
                      Save
                    </button>
                    <button
                      onClick={() => setEditingId(null)}
                      className="text-gray-600 hover:text-gray-900"
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleEdit(user)}
                      className="text-indigo-600 hover:text-indigo-900"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => handleDelete(user.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </div>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
