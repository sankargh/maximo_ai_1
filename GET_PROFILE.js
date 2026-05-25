MXServer = Java.type("psdi.server.MXServer")

//Get the userInfo from request
userInfo = request.getUserInfo()

// Get the Mbo Name from Query Parameter
mboName = request.getQueryParam("mboname")

// Get the Profile from MXServer-->MboSet-->Profile
mxServer = MXServer.getMXServer()
mboSet = mxServer.getMboSet(mboName, userInfo)
profile = mboSet.getProfile()

// useDataRestriction(java.lang.String groupname,java.lang.String app,java.lang.String siteorg)
// groupname="MAXADMIN";   app="WOTRACK";  siteorg="SITE001"
// var isDataRestrict  =   profile.useDataRestriction(groupname,app,siteorg)
// var restrictionCache = mxServer.getDataRestrictionCache()

userName = userInfo.getUserName()
defaultOrg = profile.getDefaultOrg()
defaultSite = profile.getDefaultSite()
orgWhereClause = profile.getOrgsString()
siteWhereClause = profile.getSitesString()

var resp = {
    "userName":userName,
    "mboName":mboName,
    "defaultOrg":defaultOrg,
    "defaultSite":defaultSite,
    "orgWhereClause":orgWhereClause,
    "siteWhereClause":siteWhereClause
    // "isDataRestrict":String(isDataRestrict),
    // "appSiteWhereClause":profile.getReadableSitesString("WOTRACK"),
    // "nonStandardApps": [String(profile.getNonStandardApps())]
}

var responseBody = JSON.stringify(resp);