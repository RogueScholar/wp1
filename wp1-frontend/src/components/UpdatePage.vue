<template>
  <div>
    <div class="row">
      <div class="col-xl-6">
        <Autocomplete
          :incomingSearch="incomingSearch || $route.params.projectName"
          :hideInstructions="true"
          v-on:select-project="currentProject = $event"
        ></Autocomplete>
      </div>
    </div>
    <div class="row">
      <div class="col-xl-4">
        <div v-if="currentProject && !updateTime">
          <label class="mt-2" for="confirm"
            >Proceed with manual update of <b>{{ currentProject }}</b
            >?</label
          >
          <div class="input-group">
            <button
              v-on:click="onUpdateClick()"
              class="btn-primary form-control"
            >
              Manual Update
            </button>
          </div>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col-xl-6">
        <div v-if="currentProject && updateTime">
          <p>
            Manual update of <b>{{ this.$route.params.projectName }}</b> has
            been scheduled. It can take anywhere from 2 - 200 minutes, depending
            on project size. The next update can be performed at
            <b>{{ updateTime }}</b
            >.
          </p>
          <div>
            <p>
              <b>Progress:</b>
              {{ getProgressString() }}
            </p>

            <div v-if="!jobComplete && !jobNotStarted" class="progress">
              <div
                class="progress-bar"
                role="progressbar"
                :style="{ width: progressWidth + '%' }"
                :aria-valuenow="progressCurrent"
                aria-valuemin="0"
                :aria-valuemax="progressTotal"
              ></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Autocomplete from './Autocomplete.vue';

export default {
  name: 'updatepage',
  components: {
    Autocomplete
  },
  props: ['incomingSearch'],
  data: function() {
    return {
      currentProject: null,
      updateTime: null,
      pollingId: 0,
      progressCurrent: null,
      progressTotal: null,
      jobStatusEnum: null
    };
  },
  computed: {
    currentProjectId: function() {
      if (!this.currentProject) {
        return null;
      }
      return this.currentProject.replace(/ /g, '_');
    },
    jobComplete: function() {
      return this.jobStatusEnum === 'finished';
    },
    jobFinishingUp: function() {
      return (
        this.jobStatusEnum !== null &&
        this.jobStatusEnum !== 'finished' &&
        this.progressTotal > 0 &&
        this.progressCurrent >= this.progressTotal
      );
    },
    jobNotStarted: function() {
      return this.jobStatusEnum === null || this.jobStatusEnum === 'queued';
    },
    progressWidth: function() {
      if (this.progressCurrent !== null && this.progressTotal !== null) {
        return ((this.progressCurrent * 100) / this.progressTotal).toFixed(4);
      }
      return null;
    }
  },
  watch: {
    currentProject: async function(val) {
      this.stopProgressPolling();
      if (val !== this.$route.params.projectName) {
        this.$router.push({ path: `/update/${val}` });
      }
      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/projects/${this.currentProjectId}/update/time`
      );
      const data = await response.json();
      this.updateTime = data.next_update_time;
      this.progressCurrent = null;
      this.progressTotal = null;
      this.jobStatusEnum = null;
    },
    updateTime: function(val) {
      if (val !== null) {
        this.startProgressPolling();
      } else {
        this.stopProgressPolling();
      }
    }
  },
  beforeRouteUpdate(to, from, next) {
    this.stopProgressPolling();
    next();
  },
  beforeRouteLeave: function(to, from, next) {
    this.stopProgressPolling();
    next();
  },
  methods: {
    onUpdateClick: async function() {
      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/projects/${this.currentProjectId}/update`,
        { method: 'POST' }
      );
      const data = await response.json();
      this.updateTime = data.next_update_time;
    },
    pollForProgress: async function() {
      const response = await fetch(
        `${process.env.VUE_APP_API_URL}/projects/${this.currentProjectId}/update/progress`
      );
      const data = await response.json();
      this.progressCurrent = (data.job && data.job.progress) || null;
      this.progressTotal = (data.job && data.job.total) || null;
      this.jobStatusEnum = (data.queue && data.queue.status) || null;
      if (this.jobComplete) {
        this.stopProgressPolling();
      }
    },
    getProgressString: function() {
      if (this.jobNotStarted) {
        return "Your job has been scheduled, but hasn't started yet.";
      }
      if (this.jobComplete) {
        return (
          'Your job is complete! You must wait up to an hour to start ' +
          'a new manual update.'
        );
      }
      if (this.jobFinishingUp) {
        return 'Your job is almost finished, just wrapping up some tasks.';
      }
      return 'Your job is running, track its progress below.';
    },
    startProgressPolling: function() {
      this.pollForProgress();
      this.pollingId = setInterval(() => this.pollForProgress(), 2000);
    },
    stopProgressPolling: function() {
      clearInterval(this.pollingId);
    }
  }
};
</script>

<style></style>
