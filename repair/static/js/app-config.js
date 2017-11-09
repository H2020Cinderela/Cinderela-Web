define([],
  function () {
  
    var config = {
      URL: '/' // base application URL
    };
    
    config.api = {
      base:               '/api', // base Rest-API URL
      stakeholders:       '/api/stakeholders/',
      casestudies:        '/api/casestudies/',
      qualities:          '/api/qualities',
      activitygroups:     '/api/casestudies/{0}/activitygroups',
      activities:         '/api/casestudies/{0}/activities',
      actors:             '/api/casestudies/{0}/actors',
      activitiesInGroup:  '/api/casestudies/{0}/activitygroups/{1}/activities',
      actorsInActivity:   '/api/casestudies/{0}/activitygroups/{1}/activities/{2}/actors',
      materials:          '/api/casestudies/{0}/materials',
      activityToActivity: '/api/casestudies/{0}/materials/{1}/activity2activity/',
      groupToGroup:       '/api/casestudies/{0}/materials/{1}/group2group/',
      actorToActor:       '/api/casestudies/{0}/materials/{1}/actor2actor/'
    };
  
    return config;
  }
);
