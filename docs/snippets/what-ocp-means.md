!!! info "What OCP means here"
    "OCP" names three different things in OVOS. Know which one a page is about:

    - **The OCP pipeline plugin**: matches utterances like "play some jazz" to a media
      request. See [OCP Pipeline](ocp-pipeline.md).
    - **The OCP skill base class**: `OVOSCommonPlaybackSkill`; skills built on it provide
      or embody media for the pipeline to find. See [OCP Skills](ocp-skills.md).
    - **The legacy OCP audio plugin**: `ovos-plugin-common-play`, the current default
      playback engine running inside `ovos-audio`. See [The OCP Audio Plugin](ocp-audio-plugin.md).
