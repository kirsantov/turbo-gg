import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";
import { authOptions } from "@/lib/auth";
import { getUsersAction } from "@/actions/admin-users-action";
import { UsersTable } from "@/components/admin/users-table";

const AdminPage = async () => {
  const session = await getServerSession(authOptions);

  if (!session) {
    return redirect("/login");
  }

  // Check if user is staff/admin
  const apiClient = await fetch(
    `${process.env.API_URL || "http://localhost:8000"}/api/users/me/`,
    {
      headers: {
        Authorization: `Bearer ${session.accessToken}`,
      },
    }
  );

  if (!apiClient.ok) {
    return redirect("/");
  }

  const result = await getUsersAction();

  if (!result.success) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">Admin Panel</h1>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          <p className="font-bold">Access Denied</p>
          <p>You do not have permission to access the admin panel.</p>
          <p className="text-sm mt-2">
            Only staff members can access this page.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2">Admin Panel</h1>
        <p className="text-gray-600">Manage users and system settings</p>
      </div>

      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold">User Management</h2>
        </div>
        <UsersTable initialUsers={result.data?.results || []} />
      </div>
    </div>
  );
};

export default AdminPage;
