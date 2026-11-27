import React from 'react';
import { Composition } from 'remotion';
import { HarnessPromoClip } from './HarnessPromoClip';

export const RemotionRoot: React.FC = () => (
  <Composition
    id="HarnessPromo"
    component={HarnessPromoClip}
    durationInFrames={120}
    fps={30}
    width={1080}
    height={1920}
  />
);
