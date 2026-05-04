<template>
  <div class="pet-avatar" :class="[stage, { sleeping: isSleeping }]">
    <!-- Egg Stage -->
    <div v-if="stage === 'egg'" class="avatar-egg">
      <svg viewBox="0 0 100 100" class="avatar-svg">
        <ellipse cx="50" cy="55" rx="35" ry="40" fill="#feca57"/>
        <ellipse cx="50" cy="55" rx="35" ry="40" fill="url(#eggGradient)"/>
        <defs>
          <linearGradient id="eggGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#feca57;stop-opacity:0.3" />
            <stop offset="100%" style="stop-color:#ff9f43;stop-opacity:0.3" />
          </linearGradient>
        </defs>
        <!-- Eyes closed (sleeping) -->
        <g v-if="isSleeping">
          <path d="M 35 45 Q 40 50 45 45" stroke="#333" stroke-width="2" fill="none"/>
          <path d="M 55 45 Q 60 50 65 45" stroke="#333" stroke-width="2" fill="none"/>
        </g>
        <!-- Eyes open -->
        <g v-else>
          <circle cx="40" cy="45" r="5" fill="#333"/>
          <circle cx="60" cy="45" r="5" fill="#333"/>
          <circle cx="42" cy="43" r="2" fill="white"/>
          <circle cx="62" cy="43" r="2" fill="white"/>
        </g>
        <!-- Blush -->
        <ellipse v-if="!isSleeping" cx="30" cy="55" rx="5" ry="3" fill="#ff9ff3" opacity="0.6"/>
        <ellipse v-if="!isSleeping" cx="70" cy="55" rx="5" ry="3" fill="#ff9ff3" opacity="0.6"/>
        <!-- Zzz when sleeping -->
        <g v-if="isSleeping">
          <text x="75" y="30" font-size="12" fill="#54a0ff" class="zzz">Z</text>
          <text x="82" y="22" font-size="10" fill="#54a0ff" class="zzz" style="animation-delay: 0.3s">z</text>
          <text x="87" y="16" font-size="8" fill="#54a0ff" class="zzz" style="animation-delay: 0.6s">z</text>
        </g>
      </svg>
    </div>

    <!-- Baby Stage -->
    <div v-else-if="stage === 'baby'" class="avatar-baby">
      <svg viewBox="0 0 100 100" class="avatar-svg">
        <!-- Body -->
        <ellipse cx="50" cy="60" rx="30" ry="35" fill="#74b9ff"/>
        <!-- Head -->
        <circle cx="50" cy="40" r="25" fill="#74b9ff"/>
        <!-- Ears -->
        <circle cx="30" cy="25" r="8" fill="#74b9ff"/>
        <circle cx="70" cy="25" r="8" fill="#74b9ff"/>
        <circle cx="30" cy="25" r="4" fill="#a2d2ff"/>
        <circle cx="70" cy="25" r="4" fill="#a2d2ff"/>
        <!-- Eyes -->
        <g v-if="isSleeping">
          <path d="M 40 38 Q 45 43 50 38" stroke="#333" stroke-width="2" fill="none"/>
          <path d="M 50 38 Q 55 43 60 38" stroke="#333" stroke-width="2" fill="none"/>
        </g>
        <g v-else>
          <ellipse cx="45" cy="38" rx="5" ry="7" fill="#333"/>
          <ellipse cx="55" cy="38" rx="5" ry="7" fill="#333"/>
          <circle cx="47" cy="36" r="2" fill="white"/>
          <circle cx="57" cy="36" r="2" fill="white"/>
        </g>
        <!-- Mouth -->
        <path v-if="getMoodPath()" :d="getMoodPath()" stroke="#333" stroke-width="2" fill="none"/>
        <!-- Blush -->
        <ellipse cx="35" cy="45" rx="4" ry="2" fill="#ff9ff3" opacity="0.6"/>
        <ellipse cx="65" cy="45" rx="4" ry="2" fill="#ff9ff3" opacity="0.6"/>
        <!-- Zzz -->
        <g v-if="isSleeping">
          <text x="80" y="25" font-size="10" fill="#54a0ff" class="zzz">Z</text>
          <text x="86" y="18" font-size="8" fill="#54a0ff" class="zzz" style="animation-delay: 0.3s">z</text>
        </g>
      </svg>
    </div>

    <!-- Teen Stage -->
    <div v-else-if="stage === 'teen'" class="avatar-teen">
      <svg viewBox="0 0 100 100" class="avatar-svg">
        <!-- Body -->
        <ellipse cx="50" cy="65" rx="35" ry="30" fill="#a29bfe"/>
        <!-- Head -->
        <circle cx="50" cy="40" r="28" fill="#a29bfe"/>
        <!-- Ears -->
        <polygon points="25,20 35,35 20,35" fill="#a29bfe"/>
        <polygon points="75,20 65,35 80,35" fill="#a29bfe"/>
        <!-- Eyes -->
        <g v-if="isSleeping">
          <path d="M 38 38 Q 45 45 52 38" stroke="#333" stroke-width="2" fill="none"/>
          <path d="M 48 38 Q 55 45 62 38" stroke="#333" stroke-width="2" fill="none"/>
        </g>
        <g v-else>
          <ellipse cx="45" cy="38" rx="6" ry="8" fill="#333"/>
          <ellipse cx="55" cy="38" rx="6" ry="8" fill="#333"/>
          <circle cx="47" cy="35" r="2.5" fill="white"/>
          <circle cx="57" cy="35" r="2.5" fill="white"/>
        </g>
        <!-- Mouth based on mood -->
        <path v-if="getMoodPath()" :d="getMoodPath()" stroke="#333" stroke-width="2" fill="none"/>
        <!-- Whiskers -->
        <g v-if="!isSleeping">
          <line x1="25" y1="45" x2="15" y2="43" stroke="#333" stroke-width="1"/>
          <line x1="25" y1="48" x2="15" y2="48" stroke="#333" stroke-width="1"/>
          <line x1="25" y1="51" x2="15" y2="53" stroke="#333" stroke-width="1"/>
          <line x1="75" y1="45" x2="85" y2="43" stroke="#333" stroke-width="1"/>
          <line x1="75" y1="48" x2="85" y2="48" stroke="#333" stroke-width="1"/>
          <line x1="75" y1="51" x2="85" y2="53" stroke="#333" stroke-width="1"/>
        </g>
        <!-- Zzz -->
        <g v-if="isSleeping">
          <text x="82" y="20" font-size="12" fill="#6c5ce7" class="zzz">Z</text>
          <text x="88" y="12" font-size="10" fill="#6c5ce7" class="zzz" style="animation-delay: 0.3s">z</text>
          <text x="92" y="6" font-size="8" fill="#6c5ce7" class="zzz" style="animation-delay: 0.6s">z</text>
        </g>
      </svg>
    </div>

    <!-- Adult Stage -->
    <div v-else-if="stage === 'adult'" class="avatar-adult">
      <svg viewBox="0 0 100 100" class="avatar-svg">
        <!-- Body -->
        <ellipse cx="50" cy="65" rx="38" ry="32" fill="#fd79a8"/>
        <!-- Head -->
        <circle cx="50" cy="38" r="30" fill="#fd79a8"/>
        <!-- Ears -->
        <circle cx="28" cy="20" r="10" fill="#fd79a8"/>
        <circle cx="72" cy="20" r="10" fill="#fd79a8"/>
        <circle cx="28" cy="20" r="5" fill="#fab1c9"/>
        <circle cx="72" cy="20" r="5" fill="#fab1c9"/>
        <!-- Eyes -->
        <g v-if="isSleeping">
          <path d="M 35 36 Q 43 44 51 36" stroke="#333" stroke-width="2.5" fill="none"/>
          <path d="M 49 36 Q 57 44 65 36" stroke="#333" stroke-width="2.5" fill="none"/>
        </g>
        <g v-else>
          <ellipse cx="43" cy="36" rx="7" ry="9" fill="#333"/>
          <ellipse cx="57" cy="36" rx="7" ry="9" fill="#333"/>
          <circle cx="45" cy="33" r="3" fill="white"/>
          <circle cx="59" cy="33" r="3" fill="white"/>
        </g>
        <!-- Mouth -->
        <path v-if="getMoodPath()" :d="getMoodPath()" stroke="#333" stroke-width="2.5" fill="none"/>
        <!-- Nose -->
        <ellipse v-if="!isSleeping" cx="50" cy="48" rx="4" ry="3" fill="#e84393"/>
        <!-- Blush -->
        <ellipse cx="30" cy="48" rx="6" ry="3" fill="#ff9ff3" opacity="0.5"/>
        <ellipse cx="70" cy="48" rx="6" ry="3" fill="#ff9ff3" opacity="0.5"/>
        <!-- Zzz -->
        <g v-if="isSleeping">
          <text x="85" y="15" font-size="14" fill="#e84393" class="zzz">Z</text>
          <text x="90" y="8" font-size="11" fill="#e84393" class="zzz" style="animation-delay: 0.3s">z</text>
          <text x="94" y="3" font-size="9" fill="#e84393" class="zzz" style="animation-delay: 0.6s">z</text>
        </g>
      </svg>
    </div>

    <!-- Senior Stage -->
    <div v-else-if="stage === 'senior'" class="avatar-senior">
      <svg viewBox="0 0 100 100" class="avatar-svg">
        <!-- Body -->
        <ellipse cx="50" cy="65" rx="40" ry="33" fill="#b2bec3"/>
        <!-- Head -->
        <circle cx="50" cy="38" r="32" fill="#b2bec3"/>
        <!-- Ears -->
        <circle cx="26" cy="18" r="11" fill="#b2bec3"/>
        <circle cx="74" cy="18" r="11" fill="#b2bec3"/>
        <!-- Glasses -->
        <circle cx="43" cy="36" r="9" stroke="#333" stroke-width="2" fill="none"/>
        <circle cx="57" cy="36" r="9" stroke="#333" stroke-width="2" fill="none"/>
        <line x1="52" y1="36" x2="48" y2="36" stroke="#333" stroke-width="2"/>
        <!-- Eyes behind glasses -->
        <g v-if="isSleeping">
          <path d="M 38 34 Q 43 39 48 34" stroke="#333" stroke-width="2" fill="none"/>
          <path d="M 52 34 Q 57 39 62 34" stroke="#333" stroke-width="2" fill="none"/>
        </g>
        <g v-else>
          <circle cx="43" cy="36" r="4" fill="#333"/>
          <circle cx="57" cy="36" r="4" fill="#333"/>
        </g>
        <!-- Mouth -->
        <path v-if="getMoodPath()" :d="getMoodPath()" stroke="#333" stroke-width="2" fill="none"/>
        <!-- Wrinkles -->
        <path d="M 35 50 Q 40 48 45 50" stroke="#636e72" stroke-width="1" fill="none" opacity="0.5"/>
        <path d="M 55 50 Q 60 48 65 50" stroke="#636e72" stroke-width="1" fill="none" opacity="0.5"/>
        <!-- Zzz -->
        <g v-if="isSleeping">
          <text x="85" y="12" font-size="14" fill="#636e72" class="zzz">Z</text>
          <text x="90" y="5" font-size="11" fill="#636e72" class="zzz" style="animation-delay: 0.3s">z</text>
        </g>
      </svg>
    </div>
  </div>
</template>

<script setup>
defineProps({
  stage: {
    type: String,
    default: 'egg'
  },
  isSleeping: {
    type: Boolean,
    default: false
  },
  mood: {
    type: String,
    default: 'good'
  }
})

function getMoodPath() {
  if (this.isSleeping) return null
  
  switch(this.mood) {
    case 'excellent':
    case 'good':
      return 'M 40 50 Q 50 58 60 50' // Smile
    case 'okay':
      return 'M 40 53 L 60 53' // Neutral
    case 'bad':
      return 'M 40 55 Q 50 48 60 55' // Frown
    case 'critical':
      return 'M 40 56 Q 50 47 60 56' // Very sad
    default:
      return 'M 40 52 Q 50 56 60 52' // Slight smile
  }
}
</script>

<style scoped>
.pet-avatar {
  width: 150px;
  height: 150px;
  display: flex;
  justify-content: center;
  align-items: center;
  animation: breathe 3s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
}

.avatar-svg {
  width: 100%;
  height: 100%;
}

.sleeping .avatar-svg {
  animation: sleepBreathe 4s ease-in-out infinite;
}

@keyframes sleepBreathe {
  0%, 100% { transform: scale(1) translateY(0); }
  50% { transform: scale(1.03) translateY(2px); }
}

.zzz {
  animation: float 2s ease-in-out infinite;
  opacity: 0.8;
}

@keyframes float {
  0%, 100% {
    opacity: 0;
    transform: translateY(0) translateX(0);
  }
  50% {
    opacity: 1;
    transform: translateY(-10px) translateX(5px);
  }
}
</style>
