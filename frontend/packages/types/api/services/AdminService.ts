/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { PaginatedUserAdminList } from '../models/PaginatedUserAdminList';
import type { PatchedUserAdminUpdate } from '../models/PatchedUserAdminUpdate';
import type { UserAdmin } from '../models/UserAdmin';
import type { UserAdminUpdate } from '../models/UserAdminUpdate';
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';
export class AdminService {
    constructor(public readonly httpRequest: BaseHttpRequest) {}
    /**
     * ViewSet for admin panel to manage all users.
     * Only accessible by staff/admin users.
     * @param page A page number within the paginated result set.
     * @returns PaginatedUserAdminList
     * @throws ApiError
     */
    public adminUsersList(
        page?: number,
    ): CancelablePromise<PaginatedUserAdminList> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/admin/users/',
            query: {
                'page': page,
            },
        });
    }
    /**
     * ViewSet for admin panel to manage all users.
     * Only accessible by staff/admin users.
     * @param requestBody
     * @returns UserAdmin
     * @throws ApiError
     */
    public adminUsersCreate(
        requestBody: UserAdmin,
    ): CancelablePromise<UserAdmin> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/admin/users/',
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * ViewSet for admin panel to manage all users.
     * Only accessible by staff/admin users.
     * @param id A unique integer value identifying this user.
     * @returns UserAdmin
     * @throws ApiError
     */
    public adminUsersRetrieve(
        id: number,
    ): CancelablePromise<UserAdmin> {
        return this.httpRequest.request({
            method: 'GET',
            url: '/api/admin/users/{id}/',
            path: {
                'id': id,
            },
        });
    }
    /**
     * ViewSet for admin panel to manage all users.
     * Only accessible by staff/admin users.
     * @param id A unique integer value identifying this user.
     * @param requestBody
     * @returns UserAdmin
     * @throws ApiError
     */
    public adminUsersUpdate(
        id: number,
        requestBody: UserAdminUpdate,
    ): CancelablePromise<UserAdmin> {
        return this.httpRequest.request({
            method: 'PUT',
            url: '/api/admin/users/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * ViewSet for admin panel to manage all users.
     * Only accessible by staff/admin users.
     * @param id A unique integer value identifying this user.
     * @param requestBody
     * @returns UserAdmin
     * @throws ApiError
     */
    public adminUsersPartialUpdate(
        id: number,
        requestBody?: PatchedUserAdminUpdate,
    ): CancelablePromise<UserAdmin> {
        return this.httpRequest.request({
            method: 'PATCH',
            url: '/api/admin/users/{id}/',
            path: {
                'id': id,
            },
            body: requestBody,
            mediaType: 'application/json',
        });
    }
    /**
     * ViewSet for admin panel to manage all users.
     * Only accessible by staff/admin users.
     * @param id A unique integer value identifying this user.
     * @returns void
     * @throws ApiError
     */
    public adminUsersDestroy(
        id: number,
    ): CancelablePromise<void> {
        return this.httpRequest.request({
            method: 'DELETE',
            url: '/api/admin/users/{id}/',
            path: {
                'id': id,
            },
        });
    }
}
