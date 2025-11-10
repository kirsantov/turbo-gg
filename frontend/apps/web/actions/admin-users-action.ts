"use server";

import { getServerSession } from "next-auth";
import { authOptions } from "@/lib/auth";
import { getApiClient } from "@/lib/api";

export async function getUsersAction() {
  const session = await getServerSession(authOptions);

  if (!session?.accessToken) {
    throw new Error("Not authenticated");
  }

  try {
    const client = getApiClient(session.accessToken);
    const response = await client.default.apiAdminUsersList();
    return { success: true, data: response };
  } catch (error) {
    console.error("Error fetching users:", error);
    return { success: false, error: "Failed to fetch users" };
  }
}

export async function updateUserAction(userId: number, data: any) {
  const session = await getServerSession(authOptions);

  if (!session?.accessToken) {
    throw new Error("Not authenticated");
  }

  try {
    const client = getApiClient(session.accessToken);
    const response = await client.default.apiAdminUsersPartialUpdate(
      userId,
      data
    );
    return { success: true, data: response };
  } catch (error) {
    console.error("Error updating user:", error);
    return { success: false, error: "Failed to update user" };
  }
}

export async function deleteUserAction(userId: number) {
  const session = await getServerSession(authOptions);

  if (!session?.accessToken) {
    throw new Error("Not authenticated");
  }

  try {
    const client = getApiClient(session.accessToken);
    await client.default.apiAdminUsersDestroy(userId);
    return { success: true };
  } catch (error) {
    console.error("Error deleting user:", error);
    return { success: false, error: "Failed to delete user" };
  }
}
