package com.tencent.devops.auth.service

import com.tencent.devops.auth.service.iam.PermissionProjectService
import com.tencent.devops.common.auth.api.pojo.BKAuthProjectRolesResources
import com.tencent.devops.common.auth.api.pojo.BkAuthGroup
import com.tencent.devops.common.auth.api.pojo.BkAuthGroupAndUserList
import org.springframework.beans.factory.annotation.Autowired

class BkAuthPermissionProjectService @Autowired constructor(

): PermissionProjectService {
    override fun getProjectUsers(serviceCode: String, projectCode: String, group: BkAuthGroup?): List<String> {
        return emptyList()
    }

    override fun getProjectGroupAndUserList(serviceCode: String, projectCode: String): List<BkAuthGroupAndUserList> {
        return emptyList()
    }

    override fun getUserProjects(userId: String): List<String> {
        return emptyList()
    }

    override fun isProjectUser(userId: String, projectCode: String, group: BkAuthGroup?): Boolean {
        return true
    }

    override fun createProjectUser(userId: String, projectCode: String, role: String): Boolean {
        return true
    }

    override fun getProjectRoles(projectCode: String, projectId: String): List<BKAuthProjectRolesResources> {
        return emptyList()
    }
}
